# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class solicitud(models.Model):
    _name = 'uprofe.solicitud'
    _description = 'Solicitudes'
    _order = 'dFechaSolicitud desc'
    _rec_name = 'name'

    name = fields.Char(string="Número de solicitud", size=50, required=True)
    dFechaSolicitud = fields.Date(string="Fecha de solicitud", required=True, default=fields.Date.today)
    sObservaciones = fields.Text(string="Observaciones")

    tipo_solicitud_id = fields.Many2one('uprofe.tipo_solicitud', string="Tipo de solicitud", required=True)
    estado_solicitud_id = fields.Many2one('uprofe.estado_solicitud', string="Estado de la solicitud", required=True)

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("name", "=ilike", record.name.strip())]):
                raise ValidationError("Ya existe una solicitud con este número.")

    @api.constrains('name')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.name.strip()) == 0:
                raise ValidationError("El número de solicitud no puede estar vacío.")
