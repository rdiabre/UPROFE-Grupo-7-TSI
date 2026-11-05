# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class estado_acuerdo(models.Model):
    _name = 'uprofe.estado_acuerdo'
    _description = 'Estados del Acuerdo'
    _order='name asc'
    
    name = fields.Char(string="Nombre", size=50, required=True)
    descripcion = fields.Text(string="Descripción")
    
    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("name", "=ilike", record.name.strip())]):
                raise ValidationError("Ya existe un estado de acuerdo con este nombre.")

    @api.constrains('name')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.name.strip()) == 0:
                raise ValidationError("El nombre del estado de acuerdo no puede estar vacío.")


    def write(self, vals):
        self._strip_string_values(vals)
        return super().write(vals)

    def _strip_string_values(self, vals):
        for field_name, val in vals.items():
            if isinstance(val, str):
                field = self._fields.get(field_name)
                if field and field.type in ('char', 'text'):
                    vals[field_name] = val.strip()
        return vals