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