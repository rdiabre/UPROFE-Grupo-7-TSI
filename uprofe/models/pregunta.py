# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Pregunta(models.Model):
    _name = 'uprofe.pregunta'
    _description = 'Pregunta de encuesta'
    _order = 'inum_pregunta asc'

    inum_pregunta = fields.Integer(string='Número de pregunta', required=True, default=1,
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
    @api.constrains('inum_pregunta')
    def _check_inum_pregunta(self):
        for record in self:
            if record.inum_pregunta < 1:
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
    @api.onchange('inum_pregunta')
    def _onchange_inum_pregunta(self):
        if self.inum_pregunta < 1:
            return {
                'value': {'inum_pregunta': 1},
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
            
    @api.depends('name', 'inum_pregunta', 'encuesta_id.name') #muesta a que encuesta pertenece cada pregunta
    def _compute_display_name(self):
        for record in self:
            record.display_name = "Encuesta: %s, Num Pregunta: %s, Pregunta: %s" % (
                record.encuesta_id.name or '', record.inum_pregunta, record.name or '')