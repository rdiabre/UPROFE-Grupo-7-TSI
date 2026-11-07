from odoo import models, fields, api
from odoo.exceptions import ValidationError

class libro_inv(models.Model):
    _name = 'uprofe.libro_inv'
    _description = "Libro de investigación"
    _inherits = {'uprofe.publicacion': 'iPublicacion_id'}
    
    iPublicacion_id = fields.Many2one('uprofe.publicacion', required=True, ondelete="cascade")