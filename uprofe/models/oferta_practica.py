# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OfertaPractica(models.Model):
    _name = 'uprofe.oferta_practica'
    _description = 'Oferta de práctica en empresa'
    _rec_name = 'stitulo'
    _order = 'dfecha_inicio desc'

    inum_oferta = fields.Integer(string='Nº de oferta', required=True)
    stitulo = fields.Char(string='Título', required=True)
    sdescripcion = fields.Text(string='Descripción')
    iplazas_disp = fields.Integer(string='Plazas disponibles', required=True, default=1)
    fremuneracion = fields.Float(string='Remuneración (€)', default=0.0)
    ihoras = fields.Integer(string='Horas', required=True, default=1)
    dfecha_inicio = fields.Date(string='Fecha de inicio', required=True,
                                default=fields.Date.context_today)
    dfecha_fin = fields.Date(string='Fecha de fin', required=True)
    sestado = fields.Selection([('abierta', 'Abierta'),
                                ('cerrada', 'Cerrada'),
                                ('completa', 'Completa')],
                               string='Estado', required=True, default='abierta')

    empresa_id = fields.Many2one('uprofe.empresa', string='Empresa',
                                 required=True, ondelete='restrict')
    convenio_id = fields.Many2one('uprofe.convenio_empresa', string='Convenio',
                                  required=True, ondelete='restrict')

    # constrains
    @api.constrains('inum_oferta')
    def _check_num_oferta(self):
        if self.inum_oferta <= 0:
            raise ValidationError("El número de oferta debe ser mayor que cero.")
        if self.search_count([('id', '!=', self.id),
                              ('inum_oferta', '=', self.inum_oferta)]):
            raise ValidationError("Ya existe una oferta con este número.")

    @api.constrains('iplazas_disp')
    def _check_plazas(self):
        if self.iplazas_disp < 0:
            raise ValidationError("Las plazas disponibles no pueden ser negativas.")

    @api.constrains('fremuneracion')
    def _check_remuneracion(self):
        if self.fremuneracion < 0:
            raise ValidationError("La remuneración no puede ser negativa.")

    @api.constrains('ihoras')
    def _check_horas(self):
        if self.ihoras < 0:
            raise ValidationError("Las horas no pueden ser negativas.")

    @api.constrains('dfecha_inicio', 'dfecha_fin')
    def _check_fechas(self):
        if self.dfecha_inicio and self.dfecha_fin \
                and self.dfecha_fin <= self.dfecha_inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la de inicio.")

    # onchange 
    @api.onchange('iplazas_disp')
    def _onchange_plazas(self):
        if self.iplazas_disp < 0:
            return {
                'value': {'iplazas_disp': 1},
                'warning': {'title': 'Plazas no válidas',
                            'message': 'Las plazas no pueden ser negativas; se ha puesto 1.'}
            }

    @api.onchange('fremuneracion')
    def _onchange_remuneracion(self):
        if self.fremuneracion < 0:
            return {
                'value': {'fremuneracion': 0.0},
                'warning': {'title': 'Remuneración no válida',
                            'message': 'La remuneración no puede ser negativa; se ha puesto 0.'}
            }

    @api.onchange('ihoras')
    def _onchange_horas(self):
        if self.ihoras < 0:
            return {
                'value': {'ihoras': 1},
                'warning': {'title': 'Horas no válidas',
                            'message': 'Las horas no pueden ser negativas; se ha puesto 1.'}
            }

    @api.onchange('dfecha_inicio', 'dfecha_fin')
    def _onchange_fechas(self):
        if self.dfecha_inicio and self.dfecha_fin \
                and self.dfecha_fin <= self.dfecha_inicio:
            return {
                'value': {'dfecha_fin': False},
                'warning': {'title': 'Fechas incorrectas',
                            'message': 'La fecha de fin debe ser posterior a la de inicio.'}
            }