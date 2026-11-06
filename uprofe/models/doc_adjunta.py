# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class doc_adjunta(models.Model):
    _name = 'uprofe.doc_adjunta'
    _description = 'Documentos adjuntos'
    _order = 'dFechaSubida desc'
    _rec_name = 'sName'

    sName = fields.Char(string="Número de documento", size=50, required=True)
    sNombreFichero = fields.Char(string="Nombre del fichero", size=100, required=True)
    sTipoDocumento = fields.Char(string="Tipo de documento", size=50)
    dFechaSubida = fields.Date(string="Fecha de subida", required=True, default=fields.Date.today)
    binFichero = fields.Binary(string="Fichero", attachment=True)

    oSolicitud_id = fields.Many2one('uprofe.solicitud', string="Solicitud", required=True)
