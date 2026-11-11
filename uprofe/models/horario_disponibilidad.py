
from odoo import models, fields


class HorarioDisponibilidad(models.Model):
    _inherit = "resource.calendar"

    espacio_ids = fields.Many2many(
        "uprofe.espacio",
        "uprofe_espacio_horario_rel",
        "calendar_id",
        "espacio_id",
        string="Espacios"
    )
