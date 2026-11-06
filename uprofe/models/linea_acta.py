# -*- coding: utf-8 -*-

from odoo import models, fields, api

NOTA_APROBADO = 5.0
NOTA_NOTABLE = 7.0
NOTA_SOBRESALIENTE = 9.0
NOTA_MATRICULA = 9.0     # nota mínima para la matrícula de honor (RD 1125/2003)

class LineaActa(models.Model):
    _name = 'uprofe.linea_acta'
    _description = 'UPROFE Línea de acta'
    _order = 'acta_id, iNum_linea'

    # Relaciones todas (1,1)
    # Si se borra el acta, se borran sus líneas (ondelete='cascade')
    acta_id = fields.Many2one('uprofe.acta', string="Acta", required=True, ondelete='cascade')
    convocatoria_id = fields.Many2one('uprofe.convocatoria_asignatura', string="Convocatoria", required=True, ondelete='restrict')
    expediente_id = fields.Many2one('uprofe.expediente', string="Expediente", required=True, ondelete='restrict')
    profesor_id = fields.Many2one('uprofe.profesor', string="Profesor", required=True, ondelete='restrict', help="Profesor que publica la nota")

    # numero de linea y acta PKs
    iNum_linea = fields.Integer(string="Número de línea", required=True, default=1)
    fNota = fields.Float(string="Nota", required=True, digits=(4, 1), aggregator='avg')

    # Campos relacionados: se guardan (store=True) para poder agrupar y buscar por ellos
    alumno_id = fields.Many2one(related='expediente_id.alumno_id', store=True, string="Alumno")
    asignatura_id = fields.Many2one(related='convocatoria_id.asignatura_id', store=True, string="Asignatura")
    bActa_publicada = fields.Boolean(related='acta_id.bPublicada', store=True, string="Acta publicada")

    # Campos calculados
    selCalificacion = fields.Selection([('suspenso', 'Suspenso'), ('aprobado', 'Aprobado'),('notable', 'Notable'),
                                        ('sobresaliente', 'Sobresaliente'), ('matricula', 'Matrícula de honor')],
                                       string="Calificación", compute='_compute_calificacion', store=True)
    bAprobada = fields.Boolean(string="Aprobada", compute='_compute_aprobada', store=True)

    _sql_constraints = [
        ('acta_num_linea_unique', 'unique(acta_id, "iNum_linea")', 'El número de línea ya existe en esta acta.'),
        # Un alumno (su expediente) solo puede aparecer una vez en cada acta
        ('acta_expediente_unique', 'unique(acta_id, expediente_id)', 'Este alumno ya está en el acta.'),
    ]

    # Nombre que se muestra: "Acta 7 · 3 – Osito Gominola"
    @api.depends('acta_id', 'iNum_linea', 'alumno_id')
    def _compute_display_name(self):
        for record in self:
            alumno = f"{record.alumno_id.name or ''} {record.alumno_id.sApellidos or ''}".strip()
            record.display_name = f"Acta {record.acta_id.iNum_acta} · {record.iNum_linea} - {alumno}"

    """[0, 5) suspenso, [5, 7) aprobado, [7, 9) notable, [9, 10] sobresaliente
    y matrícula de honor para las n mejores notas del acta a partir de 9 (depende de cada asignatura)
    Depende de las otras notas del acta: si cambia una, se recalculan todas."""
    @api.depends('fNota', 'acta_id.linea_ids.fNota', 'asignatura_id.iMatriculas_honor')
    def _compute_calificacion(self):
        for record in self:
            if record._es_matricula_honor():
                record.selCalificacion = 'matricula'
            elif record.fNota < NOTA_APROBADO:
                record.selCalificacion = 'suspenso'
            elif record.fNota < NOTA_NOTABLE:
                record.selCalificacion = 'aprobado'
            elif record.fNota < NOTA_SOBRESALIENTE:
                record.selCalificacion = 'notable'
            else:
                record.selCalificacion = 'sobresaliente'

    """Matrícula de honor: nota de 9 o más y entre las n mejores del acta (n lo pone la asignatura).
    Si hay empate en el último puesto y no caben todos, ninguno de los empatados la recibe,
    para no pasar del máximo."""
    def _es_matricula_honor(self):
        self.ensure_one()
        maximo = self.asignatura_id.iMatriculas_honor
        if self.fNota < NOTA_MATRICULA or maximo <= 0:
            return False
        notas = (self.acta_id.linea_ids | self).mapped('fNota')
        mejores = len([nota for nota in notas if nota > self.fNota])
        empatadas = len([nota for nota in notas if nota == self.fNota])
        return mejores + empatadas <= maximo

    # Aprobada con un 5 o más
    @api.depends('fNota')
    def _compute_aprobada(self):
        for record in self:
            record.bAprobada = record.fNota >= NOTA_APROBADO

    # Nota entre 0 y 10
    @api.constrains('fNota')
    def _check_nota(self):
        for record in self:
            if not 0 <= record.fNota <= 10:
                raise models.ValidationError("La nota debe estar entre 0 y 10.")

    # Número de línea mayor que 0
    @api.constrains('iNum_linea')
    def _check_num_linea(self):
        for record in self:
            if record.iNum_linea <= 0:
                raise models.ValidationError("El número de línea debe ser mayor que 0.")

    # Todas las líneas de un acta son de la misma convocatoria
    @api.constrains('convocatoria_id', 'acta_id')
    def _check_misma_convocatoria(self):
        for record in self:
            otras = record.acta_id.linea_ids - record
            if otras and record.convocatoria_id not in otras.mapped('convocatoria_id'):
                raise models.ValidationError("Todas las líneas de un acta deben ser de la misma convocatoria.")

    # Un acta publicada (firmada) ya no se puede modificar
    @api.constrains('fNota', 'expediente_id', 'convocatoria_id', 'profesor_id', 'acta_id')
    def _check_acta_publicada(self):
        for record in self:
            if record.acta_id.bPublicada:
                raise models.ValidationError("El acta ya está publicada: no se pueden añadir ni modificar sus notas.")

    # Un alumno que ya aprobó la asignatura en un acta publicada no puede volver a tener nota en otra
    @api.constrains('expediente_id', 'convocatoria_id')
    def _check_ya_aprobada(self):
        for record in self:
            aprobada = record._buscar_aprobada()
            if aprobada:
                raise models.ValidationError(f"El alumno ya aprobó esta asignatura en el acta {aprobada.acta_id.iNum_acta}.")

    # La nota la publica un profesor que da clase en la asignatura (que imparte alguna de sus sesiones). Si la asignatura todavía no tiene sesiones, no se comprueba.
    @api.constrains('profesor_id', 'convocatoria_id')
    def _check_profesor_imparte(self):
        for record in self:
            profesores = record.asignatura_id.sesion_ids.profesor_ids
            if profesores and record.profesor_id not in profesores:
                raise models.ValidationError(f"{record.profesor_id.name} {record.profesor_id.sApellidos} no imparte ninguna sesión de {record.asignatura_id.name}: no puede publicar su nota.")

    # Al elegir el alumno o la convocatoria, avisa si el alumno ya tiene aprobada la asignatura (se avisa antes de guardar; al guardar, _check_ya_aprobada no lo deja)
    @api.onchange('expediente_id', 'convocatoria_id')
    def _onchange_aviso_aprobada(self):
        aprobada = self._buscar_aprobada()
        if aprobada:
            return {
                'warning': {
                    'title': "Asignatura ya aprobada",
                    'message': f"Este alumno ya aprobó la asignatura en el acta {aprobada.acta_id.iNum_acta} con un {aprobada.fNota:.1f}.",
                }
            }

    # Al elegir la convocatoria, si la asignatura la imparte un solo profesor, se propone ese profesor
    @api.onchange('convocatoria_id')
    def _onchange_convocatoria_id(self):
        if self.convocatoria_id and not self.profesor_id:
            profesores = self.convocatoria_id.asignatura_id.sesion_ids.profesor_ids
            if len(profesores) == 1:
                self.profesor_id = profesores

    # Busca otra línea en la que el alumno ya aprobó la asignatura en un acta publicada (la usan la validación _check_ya_aprobada y el aviso _onchange_aviso_aprobada)
    def _buscar_aprobada(self):
        self.ensure_one()
        expediente = self.expediente_id._origin
        asignatura = self.convocatoria_id.asignatura_id._origin
        if not expediente or not asignatura:
            return self.browse()
        return self.search([
            ('id', '!=', self._origin.id),
            ('expediente_id', '=', expediente.id),
            ('asignatura_id', '=', asignatura.id),
            ('bAprobada', '=', True),
            ('bActa_publicada', '=', True),
        ], limit=1)
