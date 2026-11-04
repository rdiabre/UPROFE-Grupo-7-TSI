# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Persona(models.Model):
    _name = 'uprofe.persona'
    _description = 'UPROFE Persona'
    _order = 'name asc'
    # Herencia por delegación: cada persona tiene un contacto de Odoo
    # (res.partner) y usa sus campos como si fueran propios:
    # name (nombre), email, phone (teléfono), image_1920 (foto)...
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', string="Contacto",
                                 required=True, ondelete='cascade')

    # Campos propios de Persona
    apellidos = fields.Char(string="Apellidos", required=True)
    dni = fields.Char(string="DNI", size=9, required=True)