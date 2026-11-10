# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class Usuario(models.Model):
    _name = 'uprofe.usuario'
    _description = 'Usuarios de la app'
    _order = 'name asc'
    _inherits = {'res.users': 'users_id'}
    
    users_id = fields.Many2one('res.users', required=True)

    # Hago la validación de unicidad con api.constrains porque si se hace con _sql_constraints, es case sensitive
    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("name", "=ilike", record.name.strip())]):
                raise ValidationError("Ya existe un usuario con este nombre de usuario.");

    @api.constrains('login')
    def _check_correo_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("login", "=ilike", record.login.strip())]):
                raise ValidationError("Ya se registró un usuario con este correo electrónico.");

    # Validaciones de valores
    @api.constrains('name')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.name.strip()) == 0:
                raise ValidationError("El nombre de usuario no puede estar vacío.");

    @api.constrains('login')
    def _check_correo_not_empty(self):
        for record in self:
            if len(record.login.strip()) == 0:
                raise ValidationError("El correo electrónico no puede estar vacío.");
            
    @api.constrains('login')
    def _check_correo_format(self):
        regex_correo = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        
        for record in self:
            if not re.match(regex_correo, record.login.strip()):
                raise ValidationError("El correo electrónico no es válido.");
            
    @api.constrains('password')
    def _check_contrasena_robustez(self):
        regex_robustez = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
        
        for record in self:
            if not re.match(regex_robustez, record.password.strip()):
                raise ValidationError("La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número.");
            
    @api.constrains('password', 'name')
    def _check_contrasena_identidad(self):
        for record in self:
            if record.password.strip() == record.name.strip():
                raise ValidationError("Por seguridad, el nombre de usuario y la contraseña no pueden ser iguales.");
            
    @api.onchange('password')
    def _onchange_contrasena(self):
        regex_robustez = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
        if not re.match(regex_robustez, self.password.strip()):
            return {
                'warning': {
                    'title': 'Contraseña insegura',
                    'message': 'La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número.'
                }
            }