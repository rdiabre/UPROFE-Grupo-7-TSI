from odoo import models, fields, api
from odoo.exceptions import ValidationError

class congreso(models.Model):
    _name = 'uprofe.congreso'
    _description = "Aportación a congreso"
    _inherits = {'uprofe.publicacion': 'iPublicacion_id'}
    
    iPublicacion_id = fields.Many2one('uprofe.publicacion', required=True, ondelete="cascade")