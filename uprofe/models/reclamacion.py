# -*- coding: utf-8 -*-

from odoo import models, fields, api
MIN_MOTIVO = 20  # caracteres mínimos para explicar el motivo de la reclamación

class Reclamacion(models.Model):
    _name = 'uprofe.reclamacion'
    _description = 'UPROFE Reclamación'
    _order = 'dFecha desc, iNum_reclamacion desc'

    # Atributos del diagrama E-R (iNum_reclamacion es la clave)
    iNum_reclamacion = fields.Integer(string="Número de reclamación", required=True, copy=False, default=lambda self: self._siguiente_numero())
    dFecha = fields.Date(string="Fecha", required=True, default=fields.Date.context_today)
    sMotivo = fields.Text(string="Motivo", required=True)
    selEstado = fields.Selection([('pendiente', 'Pendiente'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada')],
                                 string="Estado", required=True, default='pendiente', readonly=True,
                                 help="Se cambia con los botones Aceptar y Rechazar")
    sResolucion = fields.Text(string="Resolución")

    # Una reclamación es sobre un acta (1,1); solo se puede reclamar un acta publicada
    acta_id = fields.Many2one('uprofe.acta', string="Acta", required=True, ondelete='cascade', domain=[('bPublicada', '=', True)])
    # Profesor que la resuelve (0,1): se indica al aceptarla o rechazarla
    profesor_id = fields.Many2one('uprofe.profesor', string="Resuelta por", ondelete='restrict')

    # Campos relacionados y calculados
    asignatura_id = fields.Many2one(related='acta_id.asignatura_id', store=True, string="Asignatura")
    iDias_pendiente = fields.Integer(string="Días pendiente", compute='_compute_dias_pendiente')

    _sql_constraints = [
        ('num_reclamacion_unique', 'unique("iNum_reclamacion")', 'Ya existe una reclamación con este número.'),
    ]

    # Número de reclamación: el siguiente al último que existe
    def _siguiente_numero(self):
        ultima = self.search([], order='iNum_reclamacion desc', limit=1)
        return ultima.iNum_reclamacion + 1 if ultima else 1

    # Nombre que se muestra: "Reclamación 4 – Acta 7"
    @api.depends('iNum_reclamacion', 'acta_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"Reclamación {record.iNum_reclamacion} - Acta {record.acta_id.iNum_acta or ''}"

    # Días que lleva sin resolverse (0 si ya está resuelta)
    @api.depends('dFecha', 'selEstado')
    def _compute_dias_pendiente(self):
        hoy = fields.Date.context_today(self)
        for record in self:
            if record.selEstado == 'pendiente' and record.dFecha:
                record.iDias_pendiente = (hoy - record.dFecha).days
            else:
                record.iDias_pendiente = 0

    # Botones Aceptar y Rechazar: cambian el estado con write(). Las validaciones comprueban que tenga resolución y profesor.
    def action_aceptar(self):
        self._comprobar_pendiente()
        self.write({'selEstado': 'aceptada'})

    def action_rechazar(self):
        self._comprobar_pendiente()
        self.write({'selEstado': 'rechazada'})

    # Solo se puede resolver una reclamación pendiente
    def _comprobar_pendiente(self):
        for record in self:
            if record.selEstado != 'pendiente':
                raise models.ValidationError("Esta reclamación ya está resuelta.")

    """Botón "Corregir notas" (solo en reclamaciones aceptadas): abre las notas del acta para que el profesor 
    corrija la del alumno. La reclamación va en el contexto ('reclamacion_id') para que la línea de acta 
    deje cambiar la nota aunque el acta esté publicada."""
    def action_corregir_notas(self):
        self.ensure_one()
        if self.selEstado != 'aceptada':
            raise models.ValidationError("Solo se pueden corregir notas de una reclamación aceptada.")
        vista = self.env.ref('uprofe.view_linea_acta_tree_correccion', raise_if_not_found=False)
        return {
            'type': 'ir.actions.act_window',
            'name': f"Corregir notas – Acta {self.acta_id.iNum_acta}",
            'res_model': 'uprofe.linea_acta',
            'view_mode': 'list',
            # La lista para corregir notas está en el PR de vistas; mientras no exista, Odoo usa una por defecto
            'views': [(vista.id if vista else False, 'list')],
            'domain': [('acta_id', '=', self.acta_id.id)],
            'context': {'reclamacion_id': self.id},
        }

    # Número de reclamación mayor que 0
    @api.constrains('iNum_reclamacion')
    def _check_num_reclamacion(self):
        for record in self:
            if record.iNum_reclamacion <= 0:
                raise models.ValidationError("El número de reclamación debe ser mayor que 0.")

    # Motivo: no vacío y suficientemente explicado
    @api.constrains('sMotivo')
    def _check_motivo(self):
        for record in self:
            motivo = (record.sMotivo or '').strip()
            if len(motivo) < MIN_MOTIVO:
                raise models.ValidationError(f"El motivo debe tener al menos {MIN_MOTIVO} caracteres.")

    # Fecha: ni futura ni anterior al examen de la convocatoria del acta
    @api.constrains('dFecha', 'acta_id')
    def _check_fecha(self):
        hoy = fields.Date.context_today(self)
        for record in self:
            if record.dFecha > hoy:
                raise models.ValidationError("La fecha de la reclamación no puede ser posterior a hoy.")
            fecha_examen = record.acta_id.convocatoria_id.dFecha
            if fecha_examen and record.dFecha < fecha_examen:
                raise models.ValidationError("La reclamación no puede ser anterior a la fecha del examen.")

    # Solo se pueden reclamar actas publicadas
    @api.constrains('acta_id')
    def _check_acta_publicada(self):
        for record in self:
            if not record.acta_id.bPublicada:
                raise models.ValidationError("Solo se pueden presentar reclamaciones sobre actas publicadas.")

    # Para resolverla (aceptarla o rechazarla) hacen falta la resolución y el profesor que la resuelve
    @api.constrains('selEstado', 'sResolucion', 'profesor_id')
    def _check_resolucion(self):
        for record in self:
            if record.selEstado != 'pendiente':
                if not (record.sResolucion or '').strip():
                    raise models.ValidationError("Hay que escribir la resolución antes de aceptar o rechazar la reclamación.")
                if not record.profesor_id:
                    raise models.ValidationError("Hay que indicar el profesor que resuelve la reclamación.")
