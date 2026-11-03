from odoo import models, fields, api
from odoo.exceptions import ValidationError

class articulo(models.Model):
    _name = 'uprofe.articulo'
    _description = "Artículo científicos"
    _inherits = {'uprofe.publicacion': 'publicacion_id'}
    
    publicacion_id = fields.Many2one('uprofe.publicacion', required=True, ondelete='cascade')
    
    revista = fields.Char(string="Revista", required=True)
    doi = fields.Char(string="DOI", required=True)
    
    @api.constrains('revista')
    def _check_revista_valido(self):
        for record in self:
            if len(record.revista.strip()) == 0:
                raise ValidationError("El nombre de la revista no puede estar vacío.")
    
    _sql_constraints = [
        (
            'publicacion_unique',
            'unique(publicacion_id)',
            'Esta publicación ya es un artículo.'
        )
    ]