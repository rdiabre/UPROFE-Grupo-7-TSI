# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class convenio(models.Model):
    _name = 'uprofe.convenio'
    _description = 'Convenios Erasmus'
    _order = 'dFechaFirma desc'
    _rec_name = 'sName'

    sName = fields.Char(string="Código del convenio", size=50, required=True)
    dFechaFirma = fields.Date(string="Fecha de firma", required=True)
    dFechaFin = fields.Date(string="Fecha de fin", required=True)

    oEstadoConvenio_id = fields.Many2one('uprofe.estado_convenio', string="Estado del convenio", required=True)

    @api.constrains('sName')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("sName", "=ilike", record.sName.strip())]):
                raise ValidationError("Ya existe un convenio con este código.")

    @api.constrains('sName')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.sName.strip()) == 0:
                raise ValidationError("El código del convenio no puede estar vacío.")

    @api.constrains('dFechaFirma', 'dFechaFin')
    def _check_fechas(self):
        for record in self:
            if record.dFechaFin < record.dFechaFirma:
                raise ValidationError("La fecha de fin no puede ser anterior a la fecha de firma.")

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