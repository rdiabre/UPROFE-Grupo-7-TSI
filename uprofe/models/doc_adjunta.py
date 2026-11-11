# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class doc_adjunta(models.Model):
    _name = 'uprofe.doc_adjunta'
    _description = 'Documentos adjuntos'
    _order = 'dFechaSubida desc'
    _rec_name = 'name'

    name = fields.Char(string="Número de documento", size=50, required=True)
    sNombreFichero = fields.Char(string="Nombre del fichero", size=100, required=True)
    sTipoDocumento = fields.Char(string="Tipo de documento", size=50)
    dFechaSubida = fields.Date(string="Fecha de subida", required=True, default=fields.Date.today)
    binFichero = fields.Binary(string="Fichero", attachment=True)

    solicitud_id = fields.Many2one('uprofe.solicitud', string="Solicitud", required=True)

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("name", "=ilike", record.name.strip())]):
                raise ValidationError("Ya existe un documento con este número.")

    @api.constrains('name')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.name.strip()) == 0:
                raise ValidationError("El número de documento no puede estar vacío.")

    @api.constrains('sNombreFichero')
    def _check_nombre_fichero_not_empty(self):
        for record in self:
            if len(record.sNombreFichero.strip()) == 0:
                raise ValidationError("El nombre del fichero no puede estar vacío.")
