# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Ubicacion(models.Model):
    _name = "uprofe.ubicacion"
    _description = "Ubicaciones geográficas UPO"

    sCod_ubicacion = fields.Char(string="Código de ubicación", required=True)

    fLatitud = fields.Float(string="Latitud", digits=(10, 7), required=True)

    fLongitud = fields.Float(string="Longitud", digits=(10, 7), required=True)

    _sql_constraints = [
        (
            "sCod_ubicacion_unique",
            'UNIQUE("sCod_ubicacion")',
            "El código de ubicación ya existe.",
        )
    ]

    #Depende de #Edificio
    edificio_ids = fields.One2many("uprofe.edificio", "ubicacion_id", string="Edificio")

    @api.constrains("fLatitud", "fLongitud")
    def _check_coordenadas(self):
        for record in self:
            if not -90 <= record.fLatitud <= 90:
                raise ValidationError("La latitud debe estar entre -90 y 90.")

            if not -180 <= record.fLongitud <= 180:
                raise ValidationError("La longitud debe estar entre -180 y 180")
