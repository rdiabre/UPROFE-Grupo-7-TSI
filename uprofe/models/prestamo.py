from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Prestamo(models.Model):
    _name = 'uprofe.prestamo'
    _description = 'Préstamo de Biblioteca'
    _rec_name = 'sNumPrestamo'

    sNumPrestamo = fields.Char(string='numero de Préstamo', required=True, copy=False)
    dFechaPrestamo = fields.Date(string='Fecha de Préstamo', default=fields.Date.context_today, required=True)
    dFechaDevolucion = fields.Date(string='Fecha de Devolucion')

    #alumno_id = fields.Many2one('uprofe.alumno', string='Alumno', required=True)
    libro_id = fields.Many2one('uprofe.libro', string='Libro', required=True)

    @api.constrains('dFechaPrestamo', 'dFechaDevolucion')
    def _check_fechas(self):
        for record in self:
            if record.dFechaDevolucion and record.dFechaDevolucion < record.dFechaPrestamo:
                raise ValidationError("La fecha de devolución no puede ser anterior a la de préstamo!")
