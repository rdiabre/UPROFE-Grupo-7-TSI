# -*- coding: utf-8 -*-

from odoo import models, fields


class Inventario(models.Model):
    _name = "uprofe.inventario"
    _description = "Inventarios UPO"

    sNum_inventario = fields.Char(string="Número de inventario", required=True)

    sObservaciones = fields.Text(string="Observaciones")

    dFecha_inventariado = fields.Date(
        string="Fecha de inventariado", required=True, default=fields.Date.context_today
    )

    espacio_id = fields.Many2one(
        "uprofe.espacio", string="Espacio", required=True, ondelete="restrict"
    )

    responsable_id = fields.Many2one(
       "uprofe.persona", string="Responsable", required=True, ondelete="restrict"
    )

    _sql_constraints = [
        (
            "num_inventario_unique",
            'UNIQUE("sNum_inventario")',
            "El número de inventario ya existe.",
        )
    ]
