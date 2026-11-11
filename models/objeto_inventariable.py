from odoo import models, fields


class ObjetoInventariable(models.Model):
    _inherit = "maintenance.equipment"

    sTipo_objeto = fields.Selection(
        [
            ("mobiliario", "Mobiliario"),
            ("equipo", "Equipo"),
        ],
        string="Tipo de objeto",
        required=True,
    )

    state = fields.Selection(
        [
            ("nuevo", "Nuevo"),
            ("seminuevo", "Seminuevo"),
            ("desgastado", "Desgastado"),
            ("averiado", "Averiado"),
            ("desaparecido", "Desaparecido"),
        ],
        string="Estado",
        required=True,
    )

    prestamo_ids = fields.One2many(
        "uprofe.prestamo.equipo", "equipo_id", string="Historial de préstamos"
    )

    inventario_linea_ids = fields.One2many(
        "uprofe.inventario.linea", "objeto_id", string="Historial de inventarios"
    )
