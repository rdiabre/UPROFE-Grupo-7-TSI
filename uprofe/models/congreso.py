from odoo import models, fields, api
from odoo.exceptions import ValidationError

TIPOS_PUBLICACION = [
    'uprofe.articulo',
    'uprofe.libro_inv',
    'uprofe.patente',
    'uprofe.congreso',
]

class congreso(models.Model):
    _name = 'uprofe.congreso'
    _description = "Aportación a congreso"
    _inherits = {'uprofe.publicacion': 'iPublicacion_id'}
    
    iPublicacion_id = fields.Many2one('uprofe.publicacion', required=True)
    
    sNombre_congreso = fields.Char('uprofe.congreso', required=True)
    sLugar = fields.Char(string="Lugar del congreso", required=True)
    
    @api.constrains('sNombre_congreso')
    def _check_nombre_congreso_valido(self):
        for record in self:
            if record.sNombre_congreso.strip() == "":
                raise ValidationError("El nombre del congreso no puede estar vacío.")
            
    @api.constrains('sLugar')
    def _check_lugar_valido(self):
        for record in self:
            if record.sLugar.strip() == "":
                raise ValidationError("El lugar no puede estar vacío.")
            
    @api.constrains('iPublicacion_id')
    def _check_publicacion_valida(self):
        for record in self:
            for modelo in TIPOS_PUBLICACION:
                dominio = [('iPublicacion_id', '=', record.iPublicacion_id.id)]
                if modelo == record._name:
                    dominio.append(('id', '!=', record.id))
                if self.env[modelo].search_count(dominio):
                    raise ValidationError(f"La publicación {record.iPublicacion_id.name} ya está asociada a un registro de {modelo}.")