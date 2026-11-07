from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

TIPOS_PUBLICACION = [
    'uprofe.articulo',
    'uprofe.libro_inv',
    'uprofe.patente',
    'uprofe.congreso',
]

class patente(models.Model):
    _name = 'uprofe.patente'
    _description = "Patente"
    _inherits = {'uprofe.publicacion': 'iPublicacion_id'}
    
    iPublicacion_id = fields.Many2one('uprofe.publicacion', required=True, ondelete="cascade")
    
    sNumero_patente(string="Número de patente", required=True)
    dFecha_concesion(string="Fecha de concesión", autodate=True, required=True)
    
    @api.constrains('sNumero_patente')
    def _check_numero_patente_unico(self):
        for record in self:
            if self.search_count([('id', '!=', record.id), ('sNumero_patente', '=ilike', record.sNumero_patente.strip())]):
                raise ValidationError("El número de patente ya está utilizado, debe ser único");
            
    @api.constrains('sNumero_patente')
    def _check_numero_patente_valido(self):
        # Sigue una regex para comprobar que sea válido en formato OMPI
        regex_ompi = r"^[A-Z]{2}\d{4,12}([A-Z]\d?)?$"
        for record in self:
            if not re.match(regex_ompi, record.sNumero_patente):
                raise ValidationError("Formato no válido. El número de patente debe seguir el formato OMPI")
            
    @api.constrains('iPublicacion_id')
    def _check_publicacion_valida(self):
        for record in self:
            for modelo in TIPOS_PUBLICACION:
                dominio = [('iPublicacion_id', '=', record.iPublicacion_id.id)]
                if modelo == record._name:
                    dominio.append(('id', '!=', record.id))
                if self.env[modelo].sudo().search_count(dominio):
                    raise ValidationError(f"La publicación {record.iPublicacion_id.name} ya está asociada a un registro de {modelo}.")