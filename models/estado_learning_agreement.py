# -*- coding: utf-8 -*-
# Autor: Isabel Cherino

from odoo import models, fields, api


class EstadoLearningAgreement(models.Model):
    """Estado de un learning agreement (borrador, aprobado...).

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
      2. unlink() impide borrar un estado con learning agreements (catalogo_mixin)
      3. copy_data() genera un nombre nuevo al duplicar (catalogo_mixin)
      4. Al marcar un estado como inicial se desmarca el anterior (estado_mixin)
      5. onchange: un estado final deja de ser inicial (estado_mixin)
      6. Nº de learning agreements ya firmados en este estado (compute con filtered)
    """
    _name = 'uprofe.estado_learning_agreement'
    _inherit = 'uprofe.estado_mixin'
    _description = 'Estado de un learning agreement'
    _campos_uso = ('learning_agreement_ids',)

    learning_agreement_ids = fields.One2many('uprofe.learning_agreement', 'estado_id', string="Learning agreements")
    iNum_firmados = fields.Integer(string="Nº firmados", compute='_compute_num_firmados')

    _sql_constraints = [
        ('nombre_unico', 'UNIQUE("sName")', 'Ya existe un estado con ese nombre.'),
    ]

    @api.depends('learning_agreement_ids.dFecha_firma')
    def _compute_num_firmados(self):
        for record in self:
            record.iNum_firmados = len(record.learning_agreement_ids.filtered('dFecha_firma'))
