# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Convenio(models.Model):
    _name = 'uprofe.convenio'
    _description = 'Convenios Erasmus'
    _order = 'dFechaFirma desc'
    _rec_name = 'sName'

    sName = fields.Char(string="Código del convenio", size=50, required=True)
    dFechaFirma = fields.Date(string="Fecha de firma", required=True)
    dFechaFin = fields.Date(string="Fecha de fin", required=True)

    oEstadoConvenio_id = fields.Many2one('uprofe.estado_convenio', string="Estado del convenio", required=True)
