
from odoo import models, fields


class ObjetoInventariable(models.Model):
    _inherit = 'maintenance.equipment'

    sTipo_objeto = fields.Selection([
        ('mobiliario', 'Mobiliario'),
        ('equipo', 'Equipo'),
    ], string='Tipo de objeto', required=True)

    sEstado = fields.Selection([
        ('nuevo', 'Nuevo'),
        ('seminuevo', 'Seminuevo'),
        ('desgastado', 'Desgastado'),
        ('averiado', 'Averiado'),
        ('desaparecido', 'Desaparecido'),
    ], string='Estado', required=True)
