from odoo import models, fields, api
from odoo.exceptions import ValidationError

class articulo(models.Model):
    _name = 'uprofe.articulo'
    _description = "Artículo científicos"
    _inherits = {'uprofe.publicacion': 'publicacion_id'}
    
    iPublicacion_id = fields.Many2one('uprofe.publicacion', required=True, ondelete='cascade')
    
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
            if self.search_count([(record.id, '!=', 'id'), (record.sDoi.strip(), '=ilike', 'sDoi')]):
                raise ValidationError("Ya existe un artículo con este doi, debe ser único.")
    
    @api.constrains('sDoi')
    def _check_doi_valido(self):
        for record in self:
            if len(record.sDoi.strip()) == 0:
                raise ValidationError("El DOI no puede estar vacío.")
    
    _sql_constraints = [
        (
            'publicacion_unique',
            'unique(publicacion_id)',
            'Esta publicación ya es un artículo.'
        )
    ]