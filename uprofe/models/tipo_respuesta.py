# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TipoRespuesta(models.Model):
    _name = 'uprofe.tipo_respuesta'
    _description = 'Tipo de respuesta'
    _order = 'name asc'

    name = fields.Char(string='Tipo', size=50, required=True)
    bconopciones = fields.Boolean(string='Con opciones', default=False)

    pregunta_ids = fields.One2many('uprofe.pregunta', 'tipo_respuesta_id', string='Preguntas')

    @api.constrains('bconopciones')
    def _check_preguntas_coherentes(self):
        for record in self:
            for pregunta in record.pregunta_ids:
                lineas = [l for l in (pregunta.sopciones or '').splitlines() if l.strip()]
                if record.bconopciones and len(lineas) < 2:
                    raise ValidationError(
                        f"No se puede marcar «Con opciones» en el tipo «{record.name}»: "
                        f"la pregunta «{pregunta.name}» no tiene al menos dos opciones. "
                        "Cambia antes el tipo de esas preguntas o crea un tipo nuevo.")
                if not record.bconopciones and lineas:
                    raise ValidationError(
                        f"No se puede quitar «Con opciones» del tipo «{record.name}»: "
                        f"la pregunta «{pregunta.name}» tiene opciones. "
                        "Cambia antes el tipo de esas preguntas o crea un tipo nuevo.")

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