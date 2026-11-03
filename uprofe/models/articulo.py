from odoo import models, fields, api
from odoo.exceptions import ValidationError

class articulo(models.Model):
    _name = 'uprofe.articulo'
    _description = "Artículo científicos"
    _inherits = {'uprofe.publicacion': 'publicacion_id'}
    
    publicacion_id = fields.Many2one('uprofe.publicacion', required=True, ondelete='cascade')
    
    revista = fields.Char(string="Revista", required=True)
    doi = fields.Char(string="DOI", required=True)
    
    @api.constrains('revista')
    def _check_revista_valido(self):
        for record in self:
            if len(record.revista.strip()) == 0:
                raise ValidationError("El nombre del artículo no puede estar vacío.")
            
    @api.constrains('doi')
    def _check_doi_unico(self):
        for record in self:
            if self.search_count([(record.id, '!=', 'id'), (record.doi.strip(), '=ilike', 'doi')]):
                raise ValidationError("Ya existe un artículo con este doi, debe ser único.")
    
    @api.constrains('doi')
    def _check_doi_valido(self):
        for record in self:
            if len(record.doi.strip()) == 0:
                raise ValidationError("El DOI no puede estar vacío.")
    
    _sql_constraints = [
        (
            'publicacion_unique',
            'unique(publicacion_id)',
            'Esta publicación ya es un artículo.'
        )
    ]
    
    def write(self, vals):
        self._strip_string_values(vals)
        return super().write(vals)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._strip_string_values(vals)
        return super().create(vals_list)

    def _strip_string_values(self, vals):
        for field_name, val in vals.items():
            if isinstance(val, str):
                field = self._fields.get(field_name)
                if field and field.type in ('char', 'text'):
                    vals[field_name] = val.strip()
        return vals