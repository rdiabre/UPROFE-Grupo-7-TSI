from odoo import models, fields, api
from odoo.exceptions import ValidationError

class proyecto_investigacion(models.Model):
    _name = 'uprofe.proyecto_investigacion'
    _description = "Proyecto de investigación"
    
    name = fields.Char(string="Código", required=True)
    titulo = fields.Char(string="Título", required=True)
    # Pasar más adelante a valor autocalculado por la suma de la financiación asociada
    presupuesto = fields.Float(string="Presupuesto", digits="Account", required=True)
    fecha_inicio = fields.Datetime(string="Fecha de inicio", autodate=True, required=True)
    fecha_fin = fields.Datetime(string="Fecha de fin", required=True)
    
    grupo_inv_id = fields.Many2one('uprofe.grupo_inv', string="Grupo de investigación", required=True)
    financiacion_ids = fields.One2many('uprofe.financiacion', 'proyecto_investigacion_id', "Financiaciones")
    publicacion_ids = fields.One2many('uprofe.publicacion', 'proyecto_investigacion_id', "Publicaciones")
    
    @api.constrains('name')
    def _check_codigo_unico(self):
        for record in self:
            if self.search_count([(record.id, '!=', 'id'), (record.name.strip(), '=', 'name')]):
                raise ValidationError("Este código ya está utilizado, debe ser único.")

    @api.constrains('name')
    def _check_codigo_valido(self):
        for record in self:
            if len(record.name.strip()) == 0:
                raise ValidationError("El código no puede estar vacío.")
            
    @api.constrains('titulo')
    def _check_titulo_valido(self):
        for record in self:
            if len(record.title.strip()) == 0:
                raise ValidationError("El título no puede estar vacío.")
            
    @api.constrains('presupuesto')
    def _check_titulo_valido(self):
        for record in self:
            if record.presupuesto <= 0:
                raise ValidationError("El presupuesto debe ser mayor a 0.")
            
    @api.constrains('fecha_inicio', 'fecha_fin')
    def _check_fechas_validas(self):
        for record in self:
            if record.fecha_fin and record.fecha_inicio:
                if record.fecha_fin <= record.fecha_inicio:
                    raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")
                
    @api.onchange('fecha_inicio', 'fecha_fin')
    def _onchange_fechas_validas(self):
        if self.fecha_fin and self.fecha_inicio:
            if self.fecha_fin <= self.fecha_inicio:
                ahora = fields.Datetime.now()
                un_dia_despues = ahora + timedelta(days=1)
                return {
                    'values': {
                        'fecha_inicio': ahora,
                        'fecha_fin': un_dia_despues                     
                    },
                    'warning': {
                        'title': 'Fechas no válidas',
                        'message': 'La fecha de fin debe ser posterior a la fecha de inicio.'
                    }
                }