# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ConvenioEmpresa(models.Model):
    _name = 'uprofe.convenio_empresa'
    _description = 'Convenio de prácticas con empresa'
    _rec_name = 'snum_convenio_practicas'
    _order = 'dfecha_firma desc'

    snum_convenio_practicas = fields.Char(string='Nº de convenio de prácticas', required=True)
    dfecha_firma = fields.Date(string='Fecha de firma', required=True,
                               default=fields.Date.context_today)
    dfecha_expiracion = fields.Date(string='Fecha de expiración', required=True)

    # ESTADO_CONVENIO del ER (convenio 0,N - estado 1,1)
    estado_convenio_id = fields.Many2one('uprofe.estado_convenio', string='Estado',
                                         required=True, ondelete='restrict')

    # Descomento cuando uprofe.oferta_practica esté en main (regulada. Depende de #37)
    # oferta_ids = fields.One2many('uprofe.oferta_practica', 'convenio_id',
    #                              string='Ofertas de práctica')

    # constrains 
    @api.constrains('snum_convenio_practicas')
    def _check_num_convenio_unique(self):
        for record in self:
            num = (record.snum_convenio_practicas or '').strip()
            if not num:
                raise ValidationError("El número de convenio no puede estar vacío.")
            if self.search_count([('id', '!=', record.id),
                                  ('snum_convenio_practicas', '=ilike', num)]):
                raise ValidationError("Ya existe un convenio con este número.")

    @api.constrains('dfecha_firma', 'dfecha_expiracion')
    def _check_fechas(self):
        for record in self:
            if record.dfecha_firma and record.dfecha_expiracion \
                    and record.dfecha_expiracion <= record.dfecha_firma:
                raise ValidationError(
                    "La fecha de expiración debe ser posterior a la fecha de firma.")

    # onchange 
    @api.onchange('dfecha_firma', 'dfecha_expiracion')
    def _onchange_fechas(self):
        if not self.dfecha_firma:
            return
        if not self.dfecha_expiracion:
            # Autocalcula la expiración (4 años después de la firma)
            self.dfecha_expiracion = fields.Date.add(self.dfecha_firma, years=4)
        elif self.dfecha_expiracion <= self.dfecha_firma:
            return {
                'value': {'dfecha_expiracion': fields.Date.add(self.dfecha_firma, years=4)},
                'warning': {
                    'title': 'Fechas incorrectas',
                    'message': 'La fecha de expiración debe ser posterior a la de firma; '
                               'se ha ajustado a 4 años después.'
                }
            }