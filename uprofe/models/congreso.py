from odoo import models, fields, api
from odoo.exceptions import ValidationError

class congreso(models.Model):
    _name = 'uprofe.congreso'
    _description = "Aportación a congreso"
    _inherits = {'uprofe.publicacion': 'iPublicacion_id'}
    
    iPublicacion_id = fields.Many2one('uprofe.publicacion', required=True, ondelete="cascade")
    
    sNombre_congreso = fields.Char('uprofe.congreso', required=True)
    sLugar = fields.Char(string="Lugar del congreso", required=True)
    
    @api.constrains('sNombre_congreso')
    def _check_nombre_congreso_valido(self):
        for record in self:
            if record.sNombre_congreso.strip() == "":
                raise ValidationError("El nombre del congreso no puede estar vacío.")