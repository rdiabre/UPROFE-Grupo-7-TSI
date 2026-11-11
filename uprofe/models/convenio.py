# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class convenio(models.Model):
    _name = 'uprofe.convenio'
    _description = 'Convenios Erasmus'
    _order = 'dFechaFirma desc'
    _rec_name = 'name'

    name = fields.Char(string="Código del convenio", size=50, required=True)
    dFechaFirma = fields.Date(string="Fecha de firma", required=True)
    dFechaFin = fields.Date(string="Fecha de fin", required=True)

    estado_convenio_id = fields.Many2one('uprofe.estado_convenio', string="Estado del convenio", required=True)

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("name", "=ilike", record.name.strip())]):
                raise ValidationError("Ya existe un convenio con este código.")

    @api.constrains('name')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.name.strip()) == 0:
                raise ValidationError("El código del convenio no puede estar vacío.")

    @api.constrains('dFechaFirma', 'dFechaFin')
    def _check_fechas(self):
        for record in self:
            if record.dFechaFin < record.dFechaFirma:
                raise ValidationError("La fecha de fin no puede ser anterior a la fecha de firma.")
