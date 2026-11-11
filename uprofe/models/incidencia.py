from odoo import models, fields


class Incidencia(models.Model):
    _inherit = "maintenance.request"

    sNum_incidencia = fields.Char(string="Número de incidencia", required=True)

    fCoste_relacionado = fields.Float(string="Coste relacionado", digits=(10, 2))

    _sql_constraints = [
        (
            "num_incidencia_unique",
            'UNIQUE("sNum_incidencia")',
            "El número de incidencia ya existe.",
        )
    ]
