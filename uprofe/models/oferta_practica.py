# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OfertaPractica(models.Model):
    _name = 'uprofe.oferta_practica'
    _description = 'Oferta de práctica en empresa'
    _order = 'dFecha_inicio desc'

    iNum_oferta = fields.Integer(string='Nº de oferta', required=True)
    name = fields.Char(string='Título', required=True)
    sDescripcion = fields.Text(string='Descripción')
    iPlazas_disp = fields.Integer(string='Plazas disponibles', required=True, default=1)
    fRemuneracion = fields.Float(string='Remuneración (€)', default=0.0)
    iHoras = fields.Integer(string='Horas', required=True, default=1)
    dFecha_inicio = fields.Date(string='Fecha de inicio', required=True)
    dFecha_fin = fields.Date(string='Fecha de fin', required=True)
    sEstado = fields.Selection([('abierta', 'Abierta'),
                                ('cerrada', 'Cerrada'),
                                ('completa', 'Completa')],
                               string='Estado', required=True, default='abierta')

    empresa_id = fields.Many2one('uprofe.empresa', string='Empresa', required=True)
    convenio_id = fields.Many2one('uprofe.convenio_empresa', string='Convenio', required=True)

    @api.constrains('name')
    def _check_titulo(self):
        for record in self:
            if record.name:
                if record.name.strip() == '':
                    raise ValidationError('El título no puede contener solo espacios.' )
                    
    @api.constrains('iNum_oferta')
    def _check_num_oferta(self):
        for record in self:
            if record.iNum_oferta <= 0:
                raise ValidationError("El número de oferta debe ser mayor que cero.")

            if self.search_count([
                ('id', '!=', record.id),
                ('iNum_oferta', '=', record.iNum_oferta)
            ]):
                raise ValidationError("Ya existe una oferta con este número.")

    @api.constrains('iPlazas_disp')
    def _check_plazas(self):
        for record in self:
            if record.iPlazas_disp < 0:
                raise ValidationError("Las plazas disponibles no pueden ser negativas.")

    @api.constrains('fRemuneracion')
    def _check_remuneracion(self):
        for record in self:
            if record.fRemuneracion < 0:
                raise ValidationError("La remuneración no puede ser negativa.")

    @api.constrains('iHoras')
    def _check_horas(self):
        for record in self:
            if record.iHoras <= 0:
                raise ValidationError("Las horas deben ser mayores que cero.")

    @api.constrains('dFecha_inicio', 'dFecha_fin')
    def _check_fechas(self):
        for record in self:
            if record.dFecha_inicio and record.dFecha_fin:
                if record.dFecha_fin <= record.dFecha_inicio:
                    raise ValidationError("La fecha de fin debe ser posterior a la de inicio.")

    @api.onchange('iPlazas_disp')
    def _onchange_plazas(self):
        if self.iPlazas_disp < 0:
            return {
                'value': {'iPlazas_disp': 1},
                'warning': {'title': 'Plazas no válidas',
                            'message': 'Las plazas no pueden ser negativas; se ha puesto 1.'}
            }

    @api.onchange('fRemuneracion')
    def _onchange_remuneracion(self):
        if self.fRemuneracion < 0:
            return {
                'value': {'fRemuneracion': 0.0},
                'warning': {'title': 'Remuneración no válida',
                            'message': 'La remuneración no puede ser negativa; se ha puesto 0.'}
            }

    @api.onchange('iHoras')
    def _onchange_horas(self):
        if self.iHoras <= 0:
            return {
                'value': {'iHoras': 1},
                'warning': {
                    'title': 'Horas no válidas',
                    'message': 'Las horas deben ser mayores que cero; se ha puesto 1.'
                }
            }

    @api.onchange('dFecha_inicio', 'dFecha_fin')
    def _onchange_fechas(self):
        if self.dFecha_inicio and self.dFecha_fin \
                and self.dFecha_fin <= self.dFecha_inicio:
            return {
                'value': {'dFecha_fin': False},
                'warning': {'title': 'Fechas incorrectas',
                            'message': 'La fecha de fin debe ser posterior a la de inicio.'}
            }