# -*- coding: utf-8 -*-
# Autora: Sandra Megolla Fernández
from odoo import models, fields, api


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

    @api.onchange('name')
    def _onchange_nombre(self):
        if self.name:
            self.name = self.name.strip().title()

    @api.onchange('sApellidos')
    def _onchange_apellidos(self):
        if self.sApellidos:
            self.sApellidos = self.sApellidos.strip().title()

    @api.onchange('sDni')
    def _onchange_dni(self):
        if self.sDni:
            self.sDni = self.sDni.strip().upper().replace(' ', '').replace('-', '')

    @api.onchange('email')
    def _onchange_correo(self):
        if self.email:
            self.email = self.email.strip().lower()

    @api.onchange('phone')
    def _onchange_telefono(self):
        if self.phone:
            self.phone = self.phone.replace(' ', '')
