# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


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

    @api.constrains('persona_id', 'name')
    def _check_nombre(self):
        for record in self:
            nombre = (record.name or '').strip()
            if not nombre:
                raise ValidationError('El nombre del tutor no puede estar vacío.')
            if len(nombre) > 50:
                raise ValidationError('El nombre del tutor no puede superar los 50 caracteres.')

    @api.constrains('persona_id', 'sApellidos')
    def _check_apellidos(self):
        for record in self:
            apellidos = (record.sApellidos or '').strip()
            if not apellidos:
                raise ValidationError('Los apellidos del tutor no pueden estar vacíos.')
            if len(apellidos) > 100:
                raise ValidationError('Los apellidos del tutor no pueden superar los 100 caracteres.')

    @api.constrains('persona_id', 'sDni')
    def _check_documento(self):
        for record in self:
            documento = record.sDni or ''
            if len(documento) != 9:
                raise ValidationError('El DNI o NIE del tutor debe tener 9 caracteres.')
            if ' ' in documento:
                raise ValidationError('El DNI o NIE del tutor no puede contener espacios.')
            # Persona conserva su comprobación completa del DNI o NIE.

    @api.constrains('persona_id', 'email')
    def _check_correo(self):
        for record in self:
            correo = (record.email or '').strip()
            if not correo:
                raise ValidationError('El correo del tutor no puede estar vacío.')
            if ' ' in correo or correo.count('@') != 1:
                raise ValidationError('El correo del tutor debe contener una arroba y no tener espacios.')
            partes = correo.split('@')
            if not partes[0] or not partes[1]:
                raise ValidationError('El correo debe tener texto antes y después de la arroba.')
            if '.' not in partes[1] or partes[1].startswith('.') or partes[1].endswith('.'):
                raise ValidationError('El dominio del correo no es válido.')

    @api.constrains('persona_id', 'phone')
    def _check_telefono(self):
        for record in self:
            telefono = (record.phone or '').replace(' ', '')
            if telefono.startswith('+34'):
                telefono = telefono[3:]
            if len(telefono) != 9:
                raise ValidationError('El teléfono debe tener 9 cifras, con el prefijo +34 opcional.')
            for caracter in telefono:
                if caracter not in '0123456789':
                    raise ValidationError('El teléfono solo puede contener cifras, con el prefijo +34 opcional.')
            if telefono[0] not in '6789':
                raise ValidationError('El teléfono debe empezar por 6, 7, 8 o 9.')

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
