# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Departamento(models.Model):
    _name = 'uprofe.departamento'
    _description = 'Departamento'

    cod_departamento = fields.Char('Código', required=True)
    name = fields.Char('Nombre', required = True)
    area_conocimiento = fields.Char('Área de conocimiento')

    ###### --------------- lo comento hasta que sepa que se han creado estos modulos ----------------------########
    
    #profesor_ids = fields.One2many('uprofe.profesor', 'departamento_id', string='Profesores')
    #grupo_inv_ids = fields.One2many('uprofe.grupo_inv', 'departamento_id', string='Grupos de investigación')

    _sql_constraints = [
        ('cod_departamento_uniq', 'unique(cod_departamento)', 'El código de departamento ya existe.'),
    ]