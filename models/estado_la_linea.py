# -*- coding: utf-8 -*-
# Autor: Isabel Cherino

from odoo import models, fields, api


class EstadoLaLinea(models.Model):
    """Estado de una línea del learning agreement (propuesta, convalidada...).

    Hereda de uprofe.estado_mixin -> uprofe.catalogo_mixin.
    Validaciones (5+):
      1. Nombre no vacío                       (catalogo_mixin)
      2. Nombre único sin distinguir mayúsculas (catalogo_mixin + SQL)
      3. Secuencia no negativa                 (catalogo_mixin)
      4. Nombre en minúsculas con guion bajo   (estado_mixin)
      5. Color entre 0 y 11                    (estado_mixin)
      6. No puede ser inicial y final a la vez (estado_mixin)
      7. Solo un estado inicial                (estado_mixin)
    Reglas de negocio ORM (5+):
      1. create()/write() normalizan el nombre a formato código (catalogo_mixin + estado_mixin)
      2. unlink() impide borrar un estado con líneas (catalogo_mixin)
      3. copy_data() genera un nombre nuevo al duplicar (catalogo_mixin)
      4. Al marcar un estado como inicial se desmarca el anterior (estado_mixin)
      5. onchange: un estado final deja de ser inicial (estado_mixin)
      6. Total de créditos reconocidos en este estado (compute con mapped)
    """
    _name = 'uprofe.estado_la_linea'
    _inherit = 'uprofe.estado_mixin'
    _description = 'Estado de una línea del learning agreement'
    _campos_uso = ('linea_ids',)

    linea_ids = fields.One2many('uprofe.la_linea', 'estado_id', string="Líneas")
    fCreditos_total = fields.Float(string="Créditos reconocidos", compute='_compute_creditos_total')

    _sql_constraints = [
        ('nombre_unico', 'UNIQUE("sName")', 'Ya existe un estado con ese nombre.'),
    ]

    @api.depends('linea_ids.fCreditos_reconocidos')
    def _compute_creditos_total(self):
        for record in self:
            record.fCreditos_total = sum(record.linea_ids.mapped('fCreditos_reconocidos'))
