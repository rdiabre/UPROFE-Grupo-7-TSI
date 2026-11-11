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
    _inherits = {'uprofe.publicacion': 'publicacion_id'}
    
    publicacion_id = fields.Many2one('uprofe.publicacion', required=True)
    
    sIsbn = fields.Char(string="ISBN", required=True)
    sEditorial = fields.Char(string="Editorial", required=True)
    
    @api.constrains('sIsbn')
    def _check_isbn_unico(self):
        for record in self:
            if self.search_count([('id', '!=', record.id), ('sIsbn', '=ilike', (record.sIsbn or '').strip())]):
                raise ValidationError("ISBN ya registrado, debe ser único.")
    
    @api.constrains('sIsbn')
    def _check_isbn_valido(self):
        for record in self:
            if (record.sIsbn or '').strip() == "":
                raise ValidationError("El ISBN no puede estar vacío.")
    
    @api.constrains('sEditorial')
    def _check_isbn_valido(self):
        for record in self:
            if (record.sEditorial or '').strip() == "":
                raise ValidationError("La editorial no puede estar vacía.")
            
    @api.constrains('publicacion_id')
    def _check_publicacion_valida(self):
        for record in self:
            for sModelo in TIPOS_PUBLICACION:
                lDominio = [('publicacion_id', '=', record.publicacion_id.id)]
                if sModelo == record._name:
                    lDominio.append(('id', '!=', record.id))
                if self.env[sModelo].search_count(lDominio):
                    raise ValidationError(f"La publicación {record.publicacion_id.name} ya está asociada a un registro de {sModelo}.")