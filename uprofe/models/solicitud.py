# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class solicitud(models.Model):
    _name = 'uprofe.solicitud'
    _description = 'Solicitudes'
    _order = 'dFechaSolicitud desc'
    _rec_name = 'sName'

    sName = fields.Char(string="Número de solicitud", size=50, required=True)
    dFechaSolicitud = fields.Date(string="Fecha de solicitud", required=True, default=fields.Date.today)
    sObservaciones = fields.Text(string="Observaciones")

    oTipoSolicitud_id = fields.Many2one('uprofe.tipo_solicitud', string="Tipo de solicitud", required=True)
    oEstadoSolicitud_id = fields.Many2one('uprofe.estado_solicitud', string="Estado de la solicitud", required=True)

    @api.constrains('sName')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("sName", "=ilike", record.sName.strip())]):
                raise ValidationError("Ya existe una solicitud con este número.")

    @api.constrains('sName')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.sName.strip()) == 0:
                raise ValidationError("El número de solicitud no puede estar vacío.")

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