# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.exceptions import ValidationError


class Espacio(models.Model):
    _name = "uprofe.espacio"
    _description = "Espacios UPO"

    sCod_espacio = fields.Char(string="Código de espacio", required=True)

    iCapacidad = fields.Integer(string="Capacidad", required=True)

    iPlanta = fields.Integer(string="Planta", required=True)

    edificio_id = fields.Many2one(
        "uprofe.edificio", string="Edificio", required=True, ondelete="restrict"
    )

    sala_estudio_ids = fields.One2many(
        "uprofe.sala_estudio", "espacio_id", string="Sala de estudio"
    )

    inventario_ids = fields.One2many(
        "uprofe.inventario", "espacio_id", string="Historial de inventarios"
    )

    _sql_constraints = [
        (
            "cod_espacio_unique",
            'UNIQUE("sCod_espacio", edificio_id)',
            "El código ya existe en el edificio.",
        )
    ]

    @api.constrains("iCapacidad")
    def _check_capacidad(self):
        for record in self:
            if self.iCapacidad <= 0:
                raise ValidationError("La capacidad tiene que ser mayor que cero.")
