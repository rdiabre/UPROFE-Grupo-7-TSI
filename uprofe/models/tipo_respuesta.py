# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TipoRespuesta(models.Model):
    _name = 'uprofe.tipo_respuesta'
    _description = 'Tipo de respuesta'
    _order = 'name asc'

    name = fields.Char(string='Tipo', size=50, required=True)
    bconopciones = fields.Boolean(string='Con opciones', default=False)

    # pregunta_ids (One2many a uprofe.pregunta) se añade cuando uprofe.pregunta esté en main

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([('id', '!=', record.id), ('name', '=ilike', record.name.strip())]):
                raise ValidationError("Ya existe un tipo de respuesta con ese nombre.")

    @api.constrains('name')
    def _check_name_not_empty(self):
        for record in self:
            if not record.name.strip():
                raise ValidationError("El nombre del tipo de respuesta no puede estar vacío.")

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