# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class UniversidadDestino(models.Model):
    _name = 'uprofe.universidad_destino'
    _description = 'Universidad de destino'
    _rec_name = 'sName'

    cod_erasmus = fields.Char(string="Código Erasmus", size=20, required=True)
    sName = fields.Char(string="Nombre", size=100, required=True)
    
    # Descomentar cuando exista Ciudad (pais_id depende de ciudad_id)
    # ciudad_id = fields.Many2one(
    #    'uprofe.ciudad',
    #    string="Ciudad",
    #    required=True,
    #    ondelete='restrict',
    # )
    #
    # pais_id = fields.Many2one(
    #    related='ciudad_id.pais_id',
    #    string="País",
    #    store=True,
    # )

    # Descomentar cuando existan Convenio, PlazaErasmus y AsignaturaDestino
    # convenio_ids = fields.One2many('uprofe.convenio', 'universidad_id', string="Convenios")
    # plaza_ids = fields.One2many('uprofe.plaza_erasmus', 'universidad_id', string="Plazas")
    # asignatura_ids = fields.One2many('uprofe.asignatura_destino', 'universidad_id', string="Asignaturas")

    _sql_constraints = [
        ('cod_erasmus_unico', 'UNIQUE(cod_erasmus)',
         'Ya existe una universidad con ese código Erasmus.'),
    ]

    @api.constrains('cod_erasmus')
    def _check_cod_erasmus(self):
        regex_codigo = r'^[A-Z0-9][A-Z0-9 \-]*$'
        for record in self:
            if not re.match(regex_codigo, (record.cod_erasmus or '').strip()):
                raise ValidationError(
                    "El código Erasmus solo admite mayúsculas, números, espacios y guiones."
                )