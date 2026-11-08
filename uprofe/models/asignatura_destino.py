# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AsignaturaDestino(models.Model):
    _name = 'uprofe.asignatura_destino'
    _description = 'Asignatura de la universidad de destino'

    cod_asig_destino = fields.Char(string="Código de la asignatura", size=30, required=True)
    sName = fields.Char(string="Nombre", size=150, required=True)
    fCreditos_ects = fields.Float(string="Créditos ECTS", required=True)

    universidad_id = fields.Many2one(
       'uprofe.universidad_destino',
       string="Universidad de destino",
       required=True,
       ondelete='restrict',
    )
    
    idioma_id = fields.Many2one(
       'uprofe.idioma',
       string="Idioma de impartición",
       required=True,
       ondelete='restrict',
    )

    linea_ids = fields.One2many('uprofe.la_linea', 'asignatura_destino_id', string="Líneas de acuerdo")

    _sql_constraints = [
        ('cod_asig_destino_unico', 'UNIQUE(cod_asig_destino)',
         'Ya existe una asignatura de destino con ese código.'),
    ]

    @api.constrains('fCreditos_ects')
    def _check_creditos_ects(self):
        for record in self:
            if record.fCreditos_ects <= 0:
                raise ValidationError("Los créditos ECTS deben ser mayores que 0.")