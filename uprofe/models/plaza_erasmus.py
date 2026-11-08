# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PlazaErasmus(models.Model):
    _name = 'uprofe.plaza_erasmus'
    _description = 'Plaza Erasmus'
    _rec_name = 'cod_plaza'

    cod_plaza = fields.Char(string="Código de la plaza", size=30, required=True)
    iDuracion_meses = fields.Integer(string="Duración (meses)", required=True)

    universidad_id = fields.Many2one(
       'uprofe.universidad_destino',
       string="Universidad de destino",
       required=True,
       ondelete='restrict',
    )

    nivel_estudios_id = fields.Many2one(
       'uprofe.nivel_estudios',
       string="Nivel de estudios",
       required=True,
       ondelete='restrict',
    )

    idioma_id = fields.Many2one(
       'uprofe.idioma',
       string="Idioma requerido",
       required=True,
       ondelete='restrict',
    )

    # convocatoria_id = fields.Many2one(
    #     'uprofe.convocatoria',
    #     string="Convocatoria",
    #     required=True,
    #     ondelete='restrict',
    # )

    _sql_constraints = [
        ('cod_plaza_unico', 'UNIQUE(cod_plaza)',
         'Ya existe una plaza con ese código.'),
    ]

    @api.constrains('iDuracion_meses')
    def _check_duracion_meses(self):
        for record in self:
            if record.iDuracion_meses <= 0:
                raise ValidationError("La duración debe ser de al menos 1 mes.")