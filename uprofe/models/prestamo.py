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

    @api.constrains('libro_id')
    def _check_libro_unico(self):
        for record in self:
            # record.libro_id.prestamo_id es la lista de todos los préstamos de ese libro.
            # Si el tamaño de esa lista es mayor que 1, hay duplicados.
            if len(record.libro_id.prestamo_id) > 1:
                raise ValidationError("Este libro ya tiene un préstamo registrado")

    @api.constrains('dFechaPrestamo', 'dFechaDevolucion')
    def _check_fechas(self):
        for record in self:
            if record.dFechaDevolucion and record.dFechaDevolucion < record.dFechaPrestamo:
                raise ValidationError("La fecha de devolución no puede ser anterior a la de préstamo!")
