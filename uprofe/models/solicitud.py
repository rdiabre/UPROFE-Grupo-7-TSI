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
