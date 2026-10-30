# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Usuario(models.Model):
    _name = 'uprofe.usuario'
    _description = 'Usuarios de la app'

    name = fields.Char(string="Nombre de usuario", required=True)
    correo = fields.Char(string="Correo electrónico", required=True)
    contrasena = fields.Char(string="Contraseña", required=True)
    # True si está activa False si no
    estado_cuenta = fields.Boolean(string="Activo", default=False)
    ultimo_acceso = fields.Datetime(string="Último acceso", autodate=True, readonly=True)
    foto = fields.Binary(string="Foto de perfil")