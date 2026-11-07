from odoo import models, fields, api
from odoo.exceptions import ValidationError

TIPOS_PUBLICACION = [
    'uprofe.articulo',
    'uprofe.libro_inv',
    'uprofe.patente',
    'uprofe.congreso',
]

class libro_inv(models.Model):
    _name = 'uprofe.libro_inv'
    _description = "Libro de investigación"
    _inherits = {'uprofe.publicacion': 'iPublicacion_id'}
    
    iPublicacion_id = fields.Many2one('uprofe.publicacion', required=True, ondelete="cascade")
    
    sIsbn = fields.Char(string="ISBN", required=True)
    sEditorial = fields.Char(string="Editorial", required=True)
    
    @api.constrains('sIsbn')
    def _check_isbn_unico(self):
        for record in self:
            if self.search_count([('id', '!=', record.id), ('sIsbn', '=ilike', record.sIsbn.strip())]):
                raise ValidationError("ISBN ya registrado, debe ser único.")
    
    @api.constrains('sIsbn')
    def _check_isbn_valido(self):
        for record in self:
            if record.sIsbn.strip() == "":
                raise ValidationError("El ISBN no puede estar vacío.")
    
    @api.constrains('sEditorial')
    def _check_isbn_valido(self):
        for record in self:
            if record.sEditorial.strip() == "":
                raise ValidationError("La editorial no puede estar vacía.")
            
    @api.constrains('iPublicacion_id')
    def _check_publicacion_valida(self):
        for record in self:
            for modelo in TIPOS_PUBLICACION:
                dominio = [('iPublicacion_id', '=', record.iPublicacion_id.id)]
                if modelo == record._name:
                    dominio.append(('id', '!=', record.id))
                if self.env[modelo].sudo().search_count(dominio):
                    raise ValidationError(f"La publicación {record.iPublicacion_id.name} ya está asociada a un registro de {modelo}.")