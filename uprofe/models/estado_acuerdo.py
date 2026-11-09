# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class estado_acuerdo(models.Model):
    _name = 'uprofe.estado_acuerdo'
    _description = 'Estados del Acuerdo'
    _order='sName asc'
    
    sName = fields.Char(string="Nombre", size=50, required=True)
    sDescripcion = fields.Text(string="Descripción")
    
    @api.constrains('sName')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("sName", "=ilike", record.sName.strip())]):
                raise ValidationError("Ya existe un estado de acuerdo con este nombre.")

    @api.constrains('sName')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.sName.strip()) == 0:
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