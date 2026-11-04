# -*- coding: utf-8 -*-

from odoo import models, fields, api

MAX_NOMBRE = 50


class TipoSesion(models.Model):
    _name = 'uprofe.tipo_sesion'
    _description = 'UPROFE Tipo de sesión'
    _order = 'name asc'

    # Clave primaria del diagrama E-R (atributo tipo_sesion). Se llama "name"
    # porque es el campo que Odoo muestra al seleccionar un tipo en otros modelos.
    name = fields.Char(string="Tipo de sesión", required=True, help="Por ejemplo: Enseñanzas Básicas, Enseñanzas Prácticas y de Desarrollo")

    # La relación con las sesiones (sesion_ids) se añadirá en el PR del modelo Sesión: One2many hacia un modelo que todavía no existe impide instalar el módulo.

    # Unicidad de la clave primaria con índice en la base de datos 
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Ya existe este tipo de sesión.'),
    ]

    # Tipo de sesión: no vacío y con máximo de caracteres (la unicidad la hace _sql_constraints)
    @api.constrains('name')
    def _check_nombre(self):
        for record in self:
            nombre = (record.name or '').strip()
            if not nombre:
                raise models.ValidationError("El tipo de sesión no puede estar vacío.")
            if len(nombre) > MAX_NOMBRE:
                raise models.ValidationError(f"El tipo de sesión no puede tener más de {MAX_NOMBRE} caracteres.")

    # Sin espacios sobrantes y con la primera letra en mayúscula
    # (así la unicidad compara bien: "prácticas" y "Prácticas" quedan iguales)
    # Siempre con "if": el onchange también se ejecuta con el campo vacío.
    @api.onchange('name')
    def _onchange_nombre(self):
        if self.name:
            self.name = self.name.strip().capitalize()