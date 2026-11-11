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

    