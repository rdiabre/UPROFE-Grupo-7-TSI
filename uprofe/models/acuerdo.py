# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Acuerdo(models.Model):
    _name = 'uprofe.acuerdo'
    _description = 'Acuerdo de prácticas'
    _rec_name = 'snum_acuerdo'
    _order = 'dfecha_inicio desc'

    snum_acuerdo = fields.Char(string='Nº de acuerdo', required=True)
    dfecha_firma = fields.Date(string='Fecha de firma', required=True,
                               default=fields.Date.context_today)
    dfecha_inicio = fields.Date(string='Fecha de inicio', required=True)
    dfecha_fin = fields.Date(string='Fecha de fin', required=True)

    alumno_id = fields.Many2one('uprofe.persona', string='Alumno',
                                required=True, ondelete='restrict')
    # Cambiar a uprofe.profesor cuando ese modelo exista
    tutor_interno_id = fields.Many2one('uprofe.persona', string='Tutor interno',
                                       required=True, ondelete='restrict')

    seguimiento_ids = fields.One2many('uprofe.seguimiento_practica', 'acuerdo_id',
                                      string='Seguimientos')

    # Descomentar cuando existan los modelos relacionados:
    # solicitud_id = fields.Many2one('uprofe.solicitud', string='Solicitud',
    #                                ondelete='restrict')          
    # estado_acuerdo_id = fields.Many2one('uprofe.estado_acuerdo', string='Estado',
    #                                     required=True, ondelete='restrict')  

    # constrains
    @api.constrains('snum_acuerdo')
    def _check_num_acuerdo(self):
        num = (self.snum_acuerdo or '').strip()
        if not num:
            raise ValidationError("El número de acuerdo no puede estar vacío.")
        if self.search_count([('id', '!=', self.id), ('snum_acuerdo', '=ilike', num)]):
            raise ValidationError("Ya existe un acuerdo con este número.")

    @api.constrains('dfecha_inicio', 'dfecha_fin')
    def _check_fechas(self):
        if self.dfecha_inicio and self.dfecha_fin \
                and self.dfecha_fin <= self.dfecha_inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la de inicio.")

    # onchange 
    @api.onchange('dfecha_inicio', 'dfecha_fin')
    def _onchange_fechas(self):
        if self.dfecha_inicio and self.dfecha_fin \
                and self.dfecha_fin <= self.dfecha_inicio:
            return {
                'value': {'dfecha_fin': False},
                'warning': {'title': 'Fechas incorrectas',
                            'message': 'La fecha de fin debe ser posterior a la de inicio.'}
            }