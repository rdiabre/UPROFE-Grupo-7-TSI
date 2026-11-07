from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

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