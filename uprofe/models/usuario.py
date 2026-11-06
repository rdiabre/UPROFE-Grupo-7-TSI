# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from passlib.context import CryptContext
import re

crypt = CryptContext(schemes=['pbkdf2_sha512'])

class Usuario(models.Model):
    _name = 'uprofe.usuario'
    _description = 'Usuarios de la app'
    _order = 'sName asc'

    sName = fields.Char(string="Nombre de usuario", size=50, required=True)
    sCorreo = fields.Char(string="Correo electrónico", required=True)
    sContrasena = fields.Char(string="Contraseña", required=True)
    sCepetir_contrasena = fields.Char(string="Repetir contraseña", required=True, store=False)
    # True si está activa False si no
    bEstado_cuenta = fields.Boolean(string="Activo", default=False)
    dUltimo_acceso = fields.Datetime(string="Último acceso", autodate=True, readonly=True)
    binFoto = fields.Binary(string="Foto de perfil")

    # Hago la validación de unicidad con api.constrains porque si se hace con _sql_constraints, es case sensitive
    @api.constrains('sName')
    def _check_name_unique(self):
        # IMPORTANTE el for porque constrains aplica al hacer importaciones (Ej: demos.csv)
        for record in self:
            if self.search_count([("id", "!=", record.id), ("sName", "=ilike", record.sName.strip())]):
                raise ValidationError("Ya existe un usuario con este nombre de usuario.");

    @api.constrains('sCorreo')
    def _check_correo_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("sCorreo", "=ilike", record.sCorreo.strip())]):
                raise ValidationError("Ya se registró un usuario con este correo electrónico.");

    # Validaciones de valores
    @api.constrains('sName')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.sName.strip()) == 0:
                raise ValidationError("El nombre de usuario no puede estar vacío.");

    @api.constrains('sCorreo')
    def _check_correo_not_empty(self):
        for record in self:
            if len(record.sCorreo.strip()) == 0:
                raise ValidationError("El correo electrónico no puede estar vacío.");
            
    @api.constrains('sCorreo')
    def _check_correo_format(self):
        regex_correo = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        
        for record in self:
            if not re.match(regex_correo, record.sCorreo.strip()):
                raise ValidationError("El correo electrónico no es válido.");
            
    @api.constrains('sContrasena')
    def _check_contrasena_robustez(self):
        regex_robustez = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
        
        for record in self:
            if not re.match(regex_robustez, record.sContrasena.strip()):
                raise ValidationError("La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número.");
            
    @api.constrains('sContrasena', 'sName')
    def _check_contrasena_identidad(self):
        for record in self:
            if record.sContrasena.strip() == record.sName.strip():
                raise ValidationError("Por seguridad, el nombre de usuario y la contraseña no pueden ser iguales.");
            
    @api.onchange('sContrasena')
    def _onchange_contrasena(self):
        if not self.sContrasena:
            return
        regex_robustez = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
        if not re.match(regex_robustez, self.sContrasena.strip()):
            return {
                'warning': {
                    'title': 'Contraseña insegura',
                    'message': 'La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número.'
                }
            }
            
    @api.onchange('sContrasena', 'sRepetir_contrasena')
    def _onchange_contrasena_coincide(self):
        if not self.sContrasena or not self.sRepetir_contrasena:
            return
        if self.sContrasena.strip() != self.sRepetir_contrasena.strip():
            return {
                'warning': {
                    'title': 'Contraseñas no coinciden',
                    'message': 'Ambas contraseñas deben coincidir.'
                }
            }
            
    # Limpiar espacios sobrantes
    def write(self, vals):
        if 'sContrasena' in vals or 'sRepetir_contrasena' in vals:
            pwd = vals.get('sContrasena')
            rep = vals.pop('sRepetir_contrasena', None)
            
            if pwd and rep and pwd.strip() != rep.strip():
                raise ValidationError("Ambas contraseñas deben coincidir.")
            if pwd:
                vals['sContrasena'] = crypt.hash(pwd)
        
        self._strip_string_values(vals)
        return super().write(vals)
    
    # Lo hago en el método create también para que aplique también al exportar datos (aunque yo solo vaya a usar write)
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            pwd = vals.get('sContrasena')
            rep = vals.pop('sRepetir_contrasena', None)
            
            if pwd and rep and pwd.strip() != rep.strip():
                raise ValidationError("Ambas contraseñas deben coincidir.")
            
            if pwd:
                vals['sContrasena'] = crypt.hash(pwd)
                
            self._strip_string_values(vals)
            
        return super().create(vals_list)
    
    # Función auxiliar para limpiar espacios en todos los campos
    def _strip_string_values(self, vals):
        for field_name, val in vals.items():
            if isinstance(val, str):
                field = self._fields.get(field_name)
                if field and field.type in ('char', 'text'):
                    vals[field_name] = val.strip()
        return vals