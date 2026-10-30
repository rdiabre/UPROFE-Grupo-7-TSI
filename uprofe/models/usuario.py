# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.Exception import ValidationError
import re

class Usuario(models.Model):
    _name = 'uprofe.usuario'
    _description = 'Usuarios de la app'

    name = fields.Char(string="Nombre de usuario", size=50, required=True)
    correo = fields.Char(string="Correo electrónico", required=True)
    contrasena = fields.Char(string="Contraseña", required=True)
    # True si está activa False si no
    estado_cuenta = fields.Boolean(string="Activo", default=False)
    ultimo_acceso = fields.Datetime(string="Último acceso", autodate=True, readonly=True)
    foto = fields.Binary(string="Foto de perfil")


    # Hago la validación de unicidad con api.constrains porque si se hace con _sql_constraints, es case sensitive
    @api.constrains('name')
    def _check_name_unique(self):
        # IMPORTANTE el for porque constrains aplica al hacer importaciones (Ej: demos.csv)
        for record in self:
            if self.search_count([("id", "!=", record.id.strip()), ("name", "=ilike", record.name.strip())]):
                raise ValidationError("Ya existe un usuario con este nombre de usuario.");

    @api.constrains('correo')
    def _check_correo_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id.strip()), ("correo", "=ilike", record.correo.strip())]):
                raise ValidationError("Ya se registró un usuario con este correo electrónico.");

    # Validaciones de valores
    @api.constrains('name')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.name.strip()) == 0:
                raise ValidationError("El nombre de usuario no puede estar vacío.");

    @api.constrains('correo')
    def _check_correo_not_empty(self):
        for record in self:
            if len(record.correo.strip()) == 0:
                raise ValidationError("El correo electrónico no puede estar vacío.");
            
    @api.constrains('correo')
    def _check_correo_format(self):
        regex_correo = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        
        for record in self:
            if not re.match(regex_correo, record.correo.strip()):
                raise ValidationError("El correo electrónico no es válido.");
            
    @api.constrains('contrasena')
    def _check_contrasena_robustez(self):
        regex_robustez = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
        
        for record in self:
            if not re.match(regex_robustez, record.contrasena.strip()):
                raise ValidationError("La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número.");
            
    @api.constrains('contrasena', 'name')
    def _check_contrasena_identidad(self):
        for record in self:
            if record.contrasena.strip() == record.name.strip():
                raise ValidationError("Por seguridad, el nombre de usuario y la contraseña no pueden ser iguales.");
            
    # Limpiar espacios sobrantes
    def write(self, vals):
        self._strip_string_values(vals)
        return super().write(vals)