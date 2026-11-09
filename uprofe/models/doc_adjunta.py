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
    
    @api.constrains('sName')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("sName", "=ilike", record.sName.strip())]):
                raise ValidationError("Ya existe un documento con este número.")

    @api.constrains('sName')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.sName.strip()) == 0:
                raise ValidationError("El número de documento no puede estar vacío.")

    @api.constrains('sNombreFichero')
    def _check_nombre_fichero_not_empty(self):
        for record in self:
            if len(record.sNombreFichero.strip()) == 0:
                raise ValidationError("El nombre del fichero no puede estar vacío.")

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
