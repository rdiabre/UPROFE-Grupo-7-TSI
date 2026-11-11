# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Laboratorio(models.Model):
    _name = 'uprofe.laboratorio'
    _description = 'Laboratorio'
    _inherits = {'uprofe.espacio': 'espacio_id'}

    espacio_id = fields.Many2one('uprofe.espacio', required=True)

    cod_espacio = fields.Char(string='Código de Espacio', required=True)
    capacidad = fields.Integer(string='Capacidad')
    planta = fields.Char(string='Planta')


    especialidad = fields.Char(
        string='Especialidad',
        required=True,
        help='Ej: Química Orgánica, Robótica, Biología Celular...'
    )
    normas_seguridad = fields.Text(
        string='Normas de Seguridad',
        help='Protocolos de protección y seguridad obligatorios en el laboratorio'
    )


    grupo_inv_ids = fields.One2many(
        comodel_name='uprofe.grupo_inv',
        inverse_name='laboratorio_id',
        string='Grupos de Investigación'
    )

    TIPOS_ESPACIO = [
    'uprofe.aula',
    'uprofe.laboratorio',
    ]
