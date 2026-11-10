# -*- coding: utf-8 -*-

from odoo import models, fields, api

# Duración mínima y máxima de las sesiones (en horas: 0.5 = media hora)
DURACION_MIN = 0.5
DURACION_MAX = 6.0

class Sesion(models.Model):
    _name = 'uprofe.sesion'
    _description = 'UPROFE Sesión'
    _order = 'dtInicio asc'

    # Asignatura de la sesión
    asignatura_id = fields.Many2one('uprofe.asignatura', string="Asignatura", required=True)
    # Tipo de sesión de la sesión
    tipo_sesion_id = fields.Many2one('uprofe.tipo_sesion', string="Tipo de sesión", required=True)
    # Profesores de la sesión. Normalmente 1, pero podrían haber más
    profesor_ids = fields.Many2many('uprofe.profesor', string="Profesores")

    # AULA (1,1) y ALUMNO (se matricula, 0,N) se añadirán cuando existan esos modelos

    # iN_sesion es PK, junto con la asignatura
    iN_sesion = fields.Integer(string="Número de sesión", required=True, default=1)

    dtInicio = fields.Datetime(string="Inicio", required=True, default=fields.Datetime.now) # Lo último viene en el enunciado de la EPD 3
    dtFin = fields.Datetime(string="Fin", required=True, default=fields.Datetime.now)

    # Campos calculados
    # Nombre que se muestra al elegir la sesión en otros modelos: "702023 · Sesión 3"
    name = fields.Char(string="Sesión", compute='_compute_name')
    fDuracion = fields.Float(string="Duración (horas)", compute='_compute_duracion', store=True) # Se usa para calcular las estadísticas del graph de Tipo_Sesion

    # El número de sesión no se puede repetir dentro de una asignatura
    _sql_constraints = [
        ('asignatura_n_sesion_unique', 'unique(asignatura_id, "iN_sesion")',
         'Ya existe una sesión con ese número en esta asignatura.'),
    ]

    @api.depends('asignatura_id', 'iN_sesion')
    def _compute_name(self):
        for record in self:
            codigo_asig = record.asignatura_id.sCod_asig 
            if not codigo_asig:
                codigo_asig = ''
            record.name = f"{codigo_asig} · Sesión {record.iN_sesion}"

    # Calcula la duración restando los segundos. total_seconds() / 3600 la pasa a horas
    @api.depends('dtInicio', 'dtFin')
    def _compute_duracion(self):
        for record in self:
            if record.dtInicio and record.dtFin:
                record.fDuracion = (record.dtFin - record.dtInicio).total_seconds() / 3600
            else:
                record.fDuracion = 0

    @api.onchange('iN_sesion')
    def onchange_n_sesion(self):
        if self.iN_sesion <= 0:
            return {
                'value': {'iN_sesion': 1},
                'warning': {
                    'title': 'Valores incorrectos',
                    'message': 'El número de sesión debe ser mayor que 0. ¿Quisiste escribir 1?'
                }
            }

    # Número de sesión mayor que 0
    @api.constrains('iN_sesion')
    def _check_n_sesion(self):
        for record in self:
            if record.iN_sesion <= 0:
                raise models.ValidationError("El número de sesión debe ser mayor que 0.")

    # El fin después del inicio, el mismo día y con una duración razonable
    @api.constrains('dtInicio', 'dtFin')
    def _check_horas(self):
        for record in self:
            if record.dtFin <= record.dtInicio:
                raise models.ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
            if record.dtInicio.date() != record.dtFin.date():
                raise models.ValidationError("La sesión debe empezar y terminar el mismo día.")
            if record.fDuracion < DURACION_MIN or record.fDuracion > DURACION_MAX:
                raise models.ValidationError(f"Una sesión debe durar entre {DURACION_MIN} y {DURACION_MAX} horas.")

    # Las sesiones son de lunes a viernes (weekday(): lunes = 0 ... sábado = 5, domingo = 6)
    @api.constrains('dtInicio')
    def _check_fecha(self):
        for record in self:
            if record.dtInicio.weekday() >= 5:
                raise models.ValidationError("No se pueden programar sesiones en sábado ni en domingo.")

    # Al menos un profesor. Se añade 'asignatura_id' para que la validación salte
    # también al crear la sesión sin profesores.
    @api.constrains('profesor_ids', 'asignatura_id')
    def _check_profesores(self):
        for record in self:
            if not record.profesor_ids:
                raise models.ValidationError("La sesión debe tener al menos un profesor.")

    # Un profesor no puede impartir dos sesiones a la vez: se solapan si una empieza
    # antes de que acabe la otra y acaba después de que empiece la otra
    @api.constrains('profesor_ids', 'dtInicio', 'dtFin')
    def _check_solapamiento(self):
        for record in self:
            solapada = self.search([
                ('id', '!=', record.id),
                ('profesor_ids', 'in', record.profesor_ids.ids),
                ('dtInicio', '<', record.dtFin),
                ('dtFin', '>', record.dtInicio),
            ], limit=1)
            if solapada:
                # &: profesores que están en las dos sesiones
                profesores = (solapada.profesor_ids & record.profesor_ids).mapped('name')
                raise models.ValidationError(f"{', '.join(profesores)} ya tiene la sesión {solapada.name} a esa hora.")

    # Al elegir la asignatura, propone el siguiente número de sesión
    @api.onchange('asignatura_id')
    def _onchange_asignatura(self):
        if self.asignatura_id:
            ultima = self.search([('asignatura_id', '=', self.asignatura_id.id)], order='iN_sesion desc', limit=1)
            if ultima:
                self.iN_sesion = ultima.iN_sesion + 1
            else:
                self.iN_sesion = 1