
# -*- coding: utf-8 -*-

from odoo import models, api, fields


class Edificio(models.Model):
    _name = 'uprofe.edificio'
    _description = 'Edificios UPO'

    _rec_name = 'sNombre'

    sNumero_edificio = fields.Char(string='Número de edificio', required=True)

    sNombre = fields.Char(string='Nombre', required=True)

    iNumero_de_espacios = fields.Integer(string="Número de espacios", compute='_compute_numero_de_espacios')

    ubicacion_id = fields.Many2one('uprofe.ubicacion', string='Ubicación', required=True, ondelete='restrict')
    espacio_ids = fields.One2many('uprofe.espacio', 'edificio_id', string='Espacios')

    _sql_constraints = [
        ('numero_edificio_unique',
         'UNIQUE("sNumero_edificio")',
         'El número de edificio ya existe.'),

        ('ubicacion_unique',
         'UNIQUE(ubicacion_id)',
         'Esta ubicación ya está asociada a otro edificio.')
    ]

    @api.depends('espacio_ids')
    def _compute_numero_de_espacios(self):
        for record in self:
            record.iNumero_de_espacios = len(record.espacio_ids)