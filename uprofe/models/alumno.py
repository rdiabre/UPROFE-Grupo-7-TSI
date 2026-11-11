# -*- coding: utf-8 -*-
from odoo import models, fields, api

ANIO_MIN_INGRESO = 1990
MAX_CURSOS = 6

class Alumno(models.Model):
    
    _name='uprofe.alumno'
    _description = 'Alumno'
    _order = 'sApellidos asc, name asc'

    _inherits = {'uprofe.persona': 'persona_id'}

    dtFechaIngreso = fields.Date(string="Fecha de ingreso", required=True)
    iCursoActual = fields.Integer(string="Curso actual", required=True, default=1, help="Curso en el que está matriculado actualmente")

    persona_id = fields.Many2one('uprofe.persona', string="Persona", required=True, ondelete='cascade')
    sesion_ids = fields.Many2many('uprofe.sesion', string="Sesiones en las que se matricula")
    #usuario_id = fields.Many2one('uprofe.usuario', string="Usuario", required=True, ondelete='restrict')

    #a añadir: relaciones con expediente (y titulación a través de él)
    iNum_sesiones = fields.Integer(string="Nº de sesiones", compute="_compute_num_sesiones")
    fHoras_matriculadas = fields.Float(string="Horas matriculadas", compute='_compute_horas_matriculadas')

    _sql_constraints = [
        ('persona_unique', 'unique(persona_id)','Esta persona ya está registrada como alumno'),
        #('usuario_unique', 'unique(usuario_id)', 'Este usuario ya está asociado a otro alumno')
    ]

    @api.depends('sesion_ids')
    def _compute_num_sesiones(self):
        for record in self:
            record.iNum_sesiones = len(record.sesion_ids)

    #la duracion de las sesiones. fDuracion está en Sesion
    @api.depends('sesion_ids.fDuracion')
    def _compute_horas_matriculadas(self):
        for record in self:
            record.fHoras_matriculadas = sum(record.sesion_ids.mapped('fDuracion'))

    #una persona es es alumno, investigador, profesor o tutor externo
    #faltaría poner tutor externo en el and
    @api.constrains('persona_id')
    def _check_no_es_otra_persona(self):
        #se parece a la comprobación hecha en grado y master, que se exluían mutuamente, pero aquí hay más opciones
        for record in self:
            if 'uprofe.investigador' in self.env and self.env['uprofe.investigador'].search_count([('persona_id', '=', record.persona_id.id)]):
                raise models.ValidationError("Esta persona ya está registrada como investigador")
            if 'uprofe.profesor' in self.env and self.env['uprofe.profesor'].search_count([('persona_id', '=', record.persona_id.id)]):
                raise models.ValidationError("Esta persona ya está registrada como profesor")
            #descomentar (y añadir código) cuando existe tutor externo
    
    @api.constrains('dtFechaIngreso')
    def _check_fecha_ingreso(self):
        hoy = fields.Date.context_today(self)
        for record in self:
            #no comprobamos si hay fecha de ingreso o no porque la exijo como required
            if record.dtFechaIngreso > hoy:
                raise models.ValidationError("La fecha de ingreso no puede ser futura")
            if record.dtFechaIngreso.year < ANIO_MIN_INGRESO:
                raise models.ValidationError(f"La fecha de ingreso no puede ser anterior a {ANIO_MIN_INGRESO}")

    @api.constrains('iCursoActual')
    def _check_curso_actual(self):
        for record in self:
            if not 1 <= record.iCursoActual <= MAX_CURSOS:
                raise models.ValidationError(f"El curso actual debe estar entre 1 y {MAX_CURSOS}")