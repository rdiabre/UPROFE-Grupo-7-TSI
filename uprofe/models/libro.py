from odoo import models, fields

class Libro(models.Model):
    _name = 'uprofe.libro'
    _description = 'Libro de la Biblioteca'

    sIsbn = fields.Char(string='ISBN', required=True)
    name = fields.Char(string='Título', required=True)
    sAutor = fields.Char(string='Autor')

    tipo = fields.Selection([
        ('texto', 'Texto'),
        ('consulta', 'Consulta'),
        ('literatura', 'Literatura')
    ], string='Tipo')

    # Relación con préstamo. 
    #prestamo_id = fields.One2many('uprofe.prestamo', 'libro_id', string='Historial de préstamos')

    #_sql_constraints = [
    #    ('prestamo_unique', 'unique(prestamo_id)', 'Este préstamo ya tiene un libro asignado.')
    #]
