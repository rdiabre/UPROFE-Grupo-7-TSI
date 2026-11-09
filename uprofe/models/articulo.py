from odoo import models, fields, api
from odoo.exceptions import ValidationError

TIPOS_PUBLICACION = [
    'uprofe.articulo',
    'uprofe.libro_inv',
    'uprofe.patente',
    'uprofe.congreso',
]

class articulo(models.Model):
    _name = 'uprofe.articulo'
    _description = "Artículo científicos"
    _inherits = {'uprofe.publicacion': 'publicacion_id'}
    
    publicacion_id = fields.Many2one('uprofe.publicacion', required=True)
    
    sRevista = fields.Char(string="Revista", required=True)
    sDoi = fields.Char(string="DOI", required=True)
    
    @api.constrains('sRevista')
    def _check_revista_valido(self):
        for record in self:
            if len(record.sRevista.strip()) == 0:
                raise ValidationError("El nombre del artículo no puede estar vacío.")
            
    @api.constrains('sDoi')
    def _check_doi_unico(self):
        for record in self:
            if self.search_count([('id', '!=', record.id), ('sDoi', '=ilike', record.sDoi.strip())]):
                raise ValidationError("Ya existe un artículo con este doi, debe ser único.")
    
    @api.constrains('sDoi')
    def _check_doi_valido(self):
        for record in self:
            if len(record.sDoi.strip()) == 0:
                raise ValidationError("El DOI no puede estar vacío.")

    @api.constrains('publicacion_id')
    def _check_publicacion_valida(self):
        for record in self:
            for sModelo in TIPOS_PUBLICACION:
                lDominio = [('publicacion_id', '=', record.publicacion_id.id)]
                if sModelo == record._name:
                    lDominio.append(('id', '!=', record.id))
                if self.env[sModelo].search_count(lDominio):
                    raise ValidationError(f"La publicación {record.publicacion_id.sName} ya está asociada a un registro de {sModelo}.")