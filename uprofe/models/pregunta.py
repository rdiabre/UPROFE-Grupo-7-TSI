# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Pregunta(models.Model):
    _name = 'uprofe.pregunta'
    _description = 'Pregunta de encuesta'
    _order = 'inumpregunta asc'

    inumpregunta = fields.Integer(string='Número de pregunta', required=True, default=1,
                                  aggregator=False)
    name = fields.Char(string='Texto de la pregunta', required=True)
    sopciones = fields.Text(string='Opciones (una por línea)')

    # TIPO_RESPUESTA del ER: modelo propio, para poder añadir tipos desde la interfaz
    tipo_respuesta_id = fields.Many2one('uprofe.tipo_respuesta', string='Tipo de respuesta',
                                        required=True, ondelete='restrict')
    bconopciones = fields.Boolean(related='tipo_respuesta_id.bconopciones')

    encuesta_id = fields.Many2one('uprofe.encuesta', string='Encuesta',
                                required=True, ondelete='cascade')
    _sql_constraints = [
        ('inumpregunta_encuesta_uniq', 'unique(encuesta_id, inumpregunta)',
        'Ya existe una pregunta con ese número en esta encuesta.'),
    ]

    # constrains
    @api.constrains('inumpregunta')
    def _check_inumpregunta(self):
        for record in self:
            if record.inumpregunta < 1:
                raise ValidationError("El número de pregunta debe ser mayor que 0.")

    @api.constrains('tipo_respuesta_id', 'sopciones')
    def _check_opciones(self):
        for record in self:
            lineas = [l for l in (record.sopciones or '').splitlines() if l.strip()]
            if record.bconopciones and len(lineas) < 2:
                raise ValidationError("Este tipo de pregunta necesita al menos dos opciones.")
            if not record.bconopciones and lineas:
                raise ValidationError("Solo los tipos que requieren opciones las admiten.")

    # onchange
    @api.onchange('inumpregunta')
    def _onchange_inumpregunta(self):
        if self.inumpregunta < 1:
            return {
                'value': {'inumpregunta': 1},
                'warning': {
                    'title': 'Valor incorrecto',
                    'message': 'El número de pregunta debe ser mayor que 0.'
                }
            }

    @api.onchange('tipo_respuesta_id')
    def _onchange_tipo_respuesta(self):
        if not self.bconopciones and self.sopciones:
            return {
                'value': {'sopciones': False},
                'warning': {
                    'title': 'Opciones eliminadas',
                    'message': 'Solo los tipos que requieren opciones las admiten.'
                }
            }