# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Movilidad(models.Model):
    _name = 'uprofe.movilidad'
    _description = 'Movilidad'
    _rec_name = 'num_movilidad'

    sNum_movilidad = fields.Char(string="Nº de movilidad", size=30, required=True)
    dFecha_inicio = fields.Date(string="Fecha de inicio", required=True)
    dFecha_fin = fields.Date(string="Fecha de fin", required=True)

    estado_id = fields.Many2one(
        'uprofe.estado_movilidad',
        string="Estado",
        required=True,
        ondelete='restrict',
    )

    # Descomentar cuando exista Solicitud (modelo de otro compañero).
    # El UNIQUE de abajo refleja el (0,1) de "origina": una solicitud origina como mucho una movilidad.
    # solicitud_id = fields.Many2one(
    #     'uprofe.solicitud',
    #     string="Solicitud de origen",
    #     required=True,
    #     ondelete='restrict',
    # )

    # Descomentar cuando exista LearningAgreement
    # learning_agreement_ids = fields.One2many(
    #     'uprofe.learning_agreement', 'movilidad_id', string="Learning agreements")

    _sql_constraints = [
        ('num_movilidad_unico', 'UNIQUE(sNum_movilidad)',
         'Ya existe una movilidad con ese número.'),
        # ('solicitud_unica', 'UNIQUE(solicitud_id)',
        #  'Esa solicitud ya ha originado una movilidad.'),
    ]

    @api.constrains('dFecha_inicio', 'dFecha_fin')
    def _check_fechas(self):
        for record in self:
            if record.dFecha_inicio and record.dFecha_fin and record.dFecha_fin < record.dFecha_inicio:
                raise ValidationError("La fecha de fin no puede ser anterior a la de inicio.")