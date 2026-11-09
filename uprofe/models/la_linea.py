# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LaLinea(models.Model):
    _name = 'uprofe.la_linea'
    _description = 'Línea de learning agreement'

    iNum_linea = fields.Integer(string="Nº de línea", required=True)
    fNota = fields.Float(string="Nota (0-10)")
    fCreditos_reconocidos = fields.Float(string="Créditos reconocidos")

    # learning_agreement_id = fields.Many2one(
    #     'uprofe.learning_agreement',
    #     string="Learning agreement",
    #     required=True,
    #     ondelete='cascade',
    # )
    # asignatura_destino_id = fields.Many2one(
    #     'uprofe.asignatura_destino',
    #     string="Asignatura de destino",
    #     required=True,
    #     ondelete='restrict',
    # )
    estado_id = fields.Many2one(
        'uprofe.estado_la_linea',
        string="Estado",
        required=True,
        ondelete='restrict',
    )

    # Descomentar cuando exista Asignatura (modelo de otro compañero)
    # asignatura_id = fields.Many2one(
    #     'uprofe.asignatura',
    #     string="Asignatura propia que se reconoce",
    #     required=True,
    #     ondelete='restrict',
    # )

    # _sql_constraints = [
    #     ('linea_unica_por_la', 'UNIQUE(learning_agreement_id, iNum_linea)',
    #      'Ya existe una línea con ese número en este learning agreement.'),
    # ]

    @api.constrains('fNota')
    def _check_nota(self):
        for record in self:
            if record.fNota and not (0 <= record.fNota <= 10):
                raise ValidationError("La nota debe estar entre 0 y 10.")

    @api.constrains('fCreditos_reconocidos')
    def _check_creditos(self):
        for record in self:
            if record.fCreditos_reconocidos < 0:
                raise ValidationError("Los créditos reconocidos no pueden ser negativos.")

    @api.constrains('estado_id', 'fNota')
    def _check_nota_si_convalidada(self):
        for record in self:
            if record.estado_id.sName == 'convalidada' and not record.fNota:
                raise ValidationError("Una línea convalidada necesita tener nota.")