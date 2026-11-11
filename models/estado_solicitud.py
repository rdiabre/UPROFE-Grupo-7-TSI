# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class estado_solicitud(models.Model):
    _name= 'uprofe.estado_solicitud'
    _description = 'Estados de la solicitud'
    _order = 'name asc'

    name = fields.Char(string="Nombre", size=50, required=True)
    sDescripcion = fields.Text(string="Descripción")

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("name", "=ilike", record.name.strip())]):
                raise ValidationError("Ya existe un estado de solicitud con este nombre.")

    @api.constrains('name')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.name.strip()) == 0:
                raise ValidationError("El nombre del estado de solicitud no puede estar vacío.")

