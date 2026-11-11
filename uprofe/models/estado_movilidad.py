# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EstadoMovilidad(models.Model):
    """Estado de una movilidad (solicitada, en_curso, finalizada...).

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
      2. unlink() impide borrar un estado con movilidades (catalogo_mixin)
      3. copy_data() genera un nombre nuevo al duplicar (catalogo_mixin)
      4. Al marcar un estado como inicial se desmarca el anterior (estado_mixin)
      5. onchange: un estado final deja de ser inicial (estado_mixin)
      6. Duración media en días de sus movilidades (compute con mapped)
    """
    _name = 'uprofe.estado_movilidad'
    _inherit = 'uprofe.estado_mixin'
    _description = 'Estado de una movilidad'
    _campos_uso = ('movilidad_ids',)

    movilidad_ids = fields.One2many('uprofe.movilidad', 'estado_id', string="Movilidades")
    fDuracion_media = fields.Float(string="Duración media (días)", compute='_compute_duracion_media', digits=(6, 1))

    _sql_constraints = [
        ('nombre_unico', 'UNIQUE("sName")', 'Ya existe un estado con ese nombre.'),
    ]

    @api.depends('movilidad_ids.iDuracion_dias')
    def _compute_duracion_media(self):
        for record in self:
            duraciones = record.movilidad_ids.mapped('iDuracion_dias')
            record.fDuracion_media = sum(duraciones) / len(duraciones) if duraciones else 0.0
