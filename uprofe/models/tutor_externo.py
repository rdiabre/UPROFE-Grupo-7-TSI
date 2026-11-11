# -*- coding: utf-8 -*-
from odoo import models, fields


class TutorExterno(models.Model):
    _name = 'uprofe.tutor_externo'
    _description = 'Tutor externo de prácticas'
    _order = 'name asc'

    _inherits = {'uprofe.persona': 'persona_id'}

    persona_id = fields.Many2one('uprofe.persona', string='Persona', required=True)

    seguimiento_ids = fields.One2many('uprofe.seguimiento_practica', 'tutor_externo_id', string='Seguimientos')

    _sql_constraints = [
        ('persona_unique', 'unique(persona_id)', 'Esta persona ya es tutor externo.'),
    ]