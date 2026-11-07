from odoo import models, fields, api
from odoo.exceptions import ValidationError

class congreso(models.Model):
    _name = 'uprofe.congreso'
    _description = "Aportación a congreso"