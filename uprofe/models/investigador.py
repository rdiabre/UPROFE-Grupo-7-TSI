# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Investigador(models.Model):
    _name='uprofe.investigador'
    _description = 'Investigador'
    _order = 'sApellidos asc, name asc'

    _inherits = {'uprofe.persona': 'persona_id'}

    persona_id = fields.Many2one('uprofe.persona', string="Persona", required=True, ondelete='cascade')
    #usuario_id = fields.Many2one('uprofe.usuario', string="Usuario", required=True, ondelete='restrict')

    linea_investigacion_ids = fields.Many2many('uprofe.linea_investigacion', string="Lineas de investigación")
    publicacion_ids = fields.Many2many('uprofe.publicacion', string="Publicaciones")

    #iNum_publicaciones = fields.Integer(string="Nº de sesiones", compute="_compute_num_publicaciones")

    _sql_constraints = [
        ('persona_unique', 'unique(persona_id)','Esta persona ya está registrada como investigador'),
        #('usuario_unique', 'unique(usuario_id)', 'Este usuario ya está asociado a otro alumno')
    ]

    