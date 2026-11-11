# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Alumno(models.Model):
    _name='uprofe.alumno'
    _description = 'Alumno'
    _order = 'sApellidos asc, name asc'

    _inherits = {'uprofe.persona': 'persona_id'}

    persona_id = fields.Many2one('uprofe.persona', string="Persona", required=True, ondelete='cascade')

    sesion_ids = fields.Many2many('uprofe.sesion', string="Sesiones en las que se matricula")

    #a añadir: relaciones con expediente (y titulación a través de él)

    iNum_sesiones = fields.Integer(string="Nº de sesiones", compute="_compute_num_sesiones")

    _sql_constrains = [
        ('persona_unique', 'unique(persona_id)','Esta persona ya está registrada como alumno')
    ]

    #una persona es es alumno, investigador, profesor o tutor externo
    #faltaría poner tutor externo en el and
    @api.constrains('persona_id')
    def _check_no_es_otra_persona(self):
        #se parece a la comprobación hecha en grado y master, que se exluían mutuamente, pero aquí hay más opciones
        for record in self:
            if 'uprofe.investigador' in self.env and self.env['uprofe.investigador'].search_count([('persona_id', '=', record.persona_id.id)]):
                raise models.ValidationsError("Esta persona ya está registrada como investigador")
            if 'uprofe.profesor' in self.env and self.env['uprofe.profesor'].search_count([('persona_id', '=', record.persona_id.id)]):
                raise models.ValidationsError("Esta persona ya está registrada como profesor")
            #descomentar (y añadir código) cuando existe tutor externo