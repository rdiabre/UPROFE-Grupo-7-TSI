
# -*- coding: utf-8 -*-

from odoo import models, fields


class Edificio(models.Model):
    _name = 'uprofe.edificio'
    _description = 'Edificios UPO'

    _rec_name = 'sNombre'

    sNumero_edificio = fields.Char(
        string='Número de edificio',
        required=True
    )

    sNombre = fields.Char(
        string='Nombre',
        required=True
    )

    #Depende de #Ubicacion
    #ubicacion_id = fields.Many2one('uprofe.ubicacion', string='Ubicación', required=True, ondelete='restrict')

    #_sql_constraints = [
     #   ('numero_edificio_unique',
      #   'UNIQUE("sNumero_edificio")',
       #  'El número de edificio ya existe.'),

        #('ubicacion_unique',
         #'UNIQUE(ubicacion_id)',
         #'Esta ubicación ya está asociada a otro edificio.')
    #]
