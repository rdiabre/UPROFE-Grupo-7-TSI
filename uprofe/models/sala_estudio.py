
# -*- coding: utf-8 -*-

from odoo import models, fields


class SalaEstudio(models.Model):
    _name = 'uprofe.sala_estudio'
    _description = 'Salas de estudio UPO'

    _inherits = {
        'uprofe.espacio': 'espacio_id'
    }

    espacio_id = fields.Many2one('uprofe.espacio', string='Espacio', required=True, ondelete='cascade')

    sTipo = fields.Char(string='Tipo', required=True)

    sRequisitos = fields.Text(string='Requisitos')

    _sql_constraints = [
        ('espacio_unique',
         'UNIQUE(espacio_id)',
         'Este espacio ya está registrado como sala de estudio.')
    ]
