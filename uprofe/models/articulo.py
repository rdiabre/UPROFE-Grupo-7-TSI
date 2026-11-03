from odoo import models, fields, api

class articulo(models.Model):
    _name = 'uprofe.articulo'
    _description = "Artículo científicos"
    _inherits = {'uprofe.publicacion': 'publicacion_id'}
    
    publicacion_id = fields.Many2one('uprofe.publicacion', required=True, ondelete='cascade')