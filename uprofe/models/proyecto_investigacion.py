from odoo import models, fields, api
from odoo.exceptions import ValidationError

class proyecto_investigacion(models.Model):
    _name = 'uprofe.proyecto_investigacion'
    _description = "Proyecto de investigación"
    
    sName = fields.Char(string="Código", required=True)
    sTitulo = fields.Char(string="Título", required=True)
    # Pasar más adelante a valor autocalculado por la suma de la financiación asociada
    fPresupuesto = fields.Float(string="Presupuesto", compute='_compute_presupuesto')
    dFecha_inicio = fields.Datetime(string="Fecha de inicio", autodate=True, required=True)
    dFecha_fin = fields.Datetime(string="Fecha de fin", required=True)
    
    iGrupo_inv_id = fields.Many2one('uprofe.grupo_inv', string="Grupo de investigación", required=True)
    lFinanciacion_ids = fields.One2many('uprofe.financiacion', 'proyecto_investigacion_id', "Financiaciones")
    lPublicacion_ids = fields.One2many('uprofe.publicacion', 'proyecto_investigacion_id', "Publicaciones")
    
    @api.constrains('sName')
    def _check_codigo_unico(self):
        for record in self:
            if self.search_count([(record.id, '!=', 'id'), (record.sName.strip(), '=ilike', 'sName')]):
                raise ValidationError("Este código ya está utilizado, debe ser único.")

    @api.constrains('sName')
    def _check_codigo_valido(self):
        for record in self:
            if len(record.sName.strip()) == 0:
                raise ValidationError("El código no puede estar vacío.")
            
    @api.constrains('sTitulo')
    def _check_titulo_valido(self):
        for record in self:
            if len(record.sTitle.strip()) == 0:
                raise ValidationError("El título no puede estar vacío.")
            
    @api.constrains('fPresupuesto')
    def _check_titulo_valido(self):
        for record in self:
            if record.fPresupuesto <= 0:
                raise ValidationError("El presupuesto debe ser mayor a 0.")
            
    @api.constrains('dFecha_inicio', 'dFecha_fin')
    def _check_fechas_validas(self):
        for record in self:
            if record.dFecha_fin and record.dFecha_inicio:
                if record.dFecha_fin <= record.dFecha_inicio:
                    raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")
                
    @api.onchange('dFecha_inicio', 'dFecha_fin')
    def _onchange_fechas_validas(self):
        if self.dFecha_fin and self.dFecha_inicio:
            if self.dFecha_fin <= self.dFecha_inicio:
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
                
    @api.depends('lFinanciacion_ids')
    def _compute_presupuesto(self):
        for record in self:
            record.presupuesto = sum(record.lFinanciacion_ids.mapped('fImporte'))