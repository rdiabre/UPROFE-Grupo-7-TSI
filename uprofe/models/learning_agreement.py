# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LearningAgreement(models.Model):
    _name = 'uprofe.learning_agreement'
    _description = 'Learning agreement'
    _rec_name = 'num_la'

    sNum_la = fields.Char(string="Nº de learning agreement", size=30, required=True)
    sVersion = fields.Integer(string="Versión", required=True, default=1)
    dFecha_firma = fields.Date(string="Fecha de firma")

    movilidad_id = fields.Many2one(
        'uprofe.movilidad',
        string="Movilidad",
        required=True,
        ondelete='restrict',
    )
    estado_id = fields.Many2one(
        'uprofe.estado_learning_agreement',
        string="Estado",
        required=True,
        ondelete='restrict',
    )

    # Descomentar cuando exista LaLinea
    # linea_ids = fields.One2many('uprofe.la_linea', 'learning_agreement_id', string="Líneas")

    _sql_constraints = [
        ('num_la_unico', 'UNIQUE(sNum_la)',
         'Ya existe un learning agreement con ese número.'),
        ('version_unica_por_movilidad', 'UNIQUE(movilidad_id, sVersion)',
         'Esa movilidad ya tiene un learning agreement con esa versión.'),
    ]

    @api.constrains('sVersion')
    def _check_version(self):
        for record in self:
            if record.sVersion < 1:
                raise ValidationError("La versión debe ser 1 o superior.")