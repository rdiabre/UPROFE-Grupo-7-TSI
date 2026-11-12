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
    
    profesor_id = fields.Many2one('uprofe.profesor', string="Profesor")
    #soy paco, he descomentado esto porque ya he hecho alumno y daba error
    alumno_id = fields.Many2one('uprofe.alumno', string="Alumno")
    
    # Validaciones para que tanto users_id, profesor_id y alumno_id solo puedan estar referenciados por una única instancia de uporfe.usuario
    _sql_constraints = [
        ('usuario_unique', 'UNIQUE(users_id)', "Este usuario ya tiene un perfil asociado"),
        ('profesor_id_unique', 'UNIQUE(profesor_id)', "Este profesor ya tiene un usuario asociado"),
        # ('alumno_id_unique', 'UNIQUE(alumno_id)', "Este alumno ya tiene un usuario asociado")
    ]

    # Hago la validación de unicidad con api.constrains porque si se hace con _sql_constraints, es case sensitive
    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("name", "=ilike", (record.name or '').strip())]):
                raise ValidationError("Ya existe un usuario con este nombre de usuario.");

    @api.constrains('login')
    def _check_correo_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("login", "=ilike", (record.login or '').strip())]):
                raise ValidationError("Ya se registró un usuario con este correo electrónico.");

    # Validaciones de valores
    @api.constrains('name')
    def _check_name_not_empty(self):
        for record in self:
            if len((record.name or '').strip()) == 0:
                raise ValidationError("El nombre de usuario no puede estar vacío.");

    @api.constrains('login')
    def _check_correo_not_empty(self):
        for record in self:
            if len((record.login or '').strip()) == 0:
                raise ValidationError("El correo electrónico no puede estar vacío.");
            
    @api.constrains('login')
    def _check_correo_format(self):
        regex_correo = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        
        for record in self:
            if not re.match(regex_correo, (record.login or '').strip()):
                raise ValidationError("El correo electrónico no es válido.");
            