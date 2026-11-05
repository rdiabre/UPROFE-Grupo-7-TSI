# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class estado_convenio(models.Model):
    _name= 'uprofe.estado_convenio'
    _description = 'Estados de convenio'
    _order = 'name asc'
    
    name= fields.Char(string='Nombre',size=50, required=True)
    descripcion=fields.Text(string="Descripción")
    
    #El nombre del estado de convenio debe ser único
    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("name", "ilike", record.name.strip())]):
                raise ValidationError("El nombre del estado de convenio debe ser único.")
    
    #El nombre del estado de convenio no puede estar vacío
    @api.constrains('name')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.name.strip()) == 0:
                raise ValidationError("El nombre del estado no puede estar vacío.")

    def write(self, vals):
        self._strip_string_values(vals)
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._strip_string_values(vals)
        return super().create(vals_list)

    def _strip_string_values(self, vals):
        for field_name, val in vals.items():
            if isinstance(val, str):
                field = self._fields.get(field_name)
                if field and field.type in ('char', 'text'):
                    vals[field_name] = val.strip()
        return vals