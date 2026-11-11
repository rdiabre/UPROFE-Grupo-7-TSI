# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class tipo_convocatoria(models.Model):
    _name = 'uprofe.tipo_convocatoria'
    _description = 'Tipos de convocatoria'
    _order = 'name asc'

    name = fields.Char(string="Nombre", size=50, required=True)
    sDescripcion = fields.Text(string="Descripción")

    
    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("name", "=ilike", record.name.strip())]):
                raise ValidationError("Ya existe un tipo de convocatoria con este nombre.")

    @api.constrains('name')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.name.strip()) == 0:
                raise ValidationError("El nombre del tipo de convocatoria no puede estar vacío.")

