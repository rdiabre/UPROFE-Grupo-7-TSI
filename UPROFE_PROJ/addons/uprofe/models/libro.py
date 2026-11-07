from odoo import models, fields

class Libro(models.Model):
    _name = 'uprofe.libro'
    _description = 'Libro de la Biblioteca'

    isbn = fields.Char(string='ISBN', required=True)
    name = fields.Char(string='Título', required=True)
    autor = fields.Char(string='Autor')
    tipo = fields.Selection([
        ('texto', 'Texto'),
        ('consulta', 'Consulta'),
        ('literatura', 'Literatura')
    ], string='Tipo')

    # Relación con préstamo. 
    prestamo_id = fields.Many2one('uprofe.prestamo', string='Préstamo actual')

    _sql_constraints = [
        ('prestamo_unique', 'unique(prestamo_id)', 'Este préstamo ya tiene un libro asignado.')
    ]