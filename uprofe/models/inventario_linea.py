from odoo import models, fields


class InventarioLinea(models.Model):
    _name = "uprofe.inventario.linea"
    _description = "Líneas de inventario UPO"

    bEncontrado = fields.Boolean(string="Encontrado", default=False)

    sObservaciones = fields.Text(string="Observaciones")

    inventario_id = fields.Many2one(
        "uprofe.inventario", string="Inventario", required=True, ondelete="cascade"
    )

    objeto_id = fields.Many2one(
        "maintenance.equipment",
        string="Objeto inventariable",
        required=True,
        ondelete="restrict",
        domain=[("sTipo_objeto", "in", ["mobiliario", "equipo"])],
    )

    _sql_constraints = [
        (
            "inventario_objeto_unique",
            "UNIQUE(inventario_id, objeto_id)",
            "Este objeto ya está incluido en el inventario.",
        )
    ]
