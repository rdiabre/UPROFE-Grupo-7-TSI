from odoo import models, fields


class PrestamoEquipo(models.Model):
    _name = "uprofe.prestamo.equipo"
    _description = "Préstamos de equipos UPO"


    equipo_id = fields.Many2one(
        "maintenance.equipment",
        string="Equipo",
        required=True,
        ondelete="restrict",
        domain=[("sTipo_objeto", "=", "equipo")]
    )

    #Depndencia con alumno
    """
    alumno_id = fields.Many2one(
        "uprofe.alumno",
        string="Alumno",
        required=True,
        ondelete="restrict"
    )
    """
    dFecha_prestamo = fields.Date(
        string="Fecha de préstamo", required=True, default=fields.Date.context_today
    )

    dFecha_devolucion = fields.Date(string="Fecha de devolución")
