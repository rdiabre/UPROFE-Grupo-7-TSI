# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Pregunta(models.Model):
    _name = 'uprofe.pregunta'
    _description = 'Pregunta de encuesta'
    _order = 'iNum_pregunta asc'

    iNum_pregunta = fields.Integer(string='Número de pregunta', required=True, default=1)
    name = fields.Char(string='Texto de la pregunta', required=True)
    sOpciones = fields.Text(string='Opciones (una por línea)')

    tipo_respuesta_id = fields.Many2one('uprofe.tipo_respuesta', string='Tipo de respuesta', required=True)
    encuesta_id = fields.Many2one('uprofe.encuesta', string='Encuesta', required=True)

    respuesta_ids = fields.One2many('uprofe.respuesta_alumno', 'pregunta_id', string='Respuestas')

    _sql_constraints = [
        ('iNum_pregunta_encuesta_uniq', 'unique(encuesta_id, "iNum_pregunta")', 'Ya existe una pregunta con ese número en esta encuesta.'),
    ]

    @api.constrains('iNum_pregunta')
    def _check_iNum_pregunta(self):
        for record in self:
            if record.iNum_pregunta < 1:
                raise ValidationError("El número de pregunta debe ser mayor que 0.")

    @api.constrains('name')
    def _check_texto(self):
        for record in self:
            if record.name:
                if record.name.strip() == '':
                    raise ValidationError('El texto de la pregunta no puede contener solo espacios.' )

    @api.constrains('sOpciones', 'tipo_respuesta_id')
    def _check_opciones(self):
        for record in self:
            if record.tipo_respuesta_id.bCon_opciones:
                if not record.sOpciones:
                    raise ValidationError('Este tipo de respuesta requiere indicar opciones.' )

                if record.sOpciones.strip() == '':
                    raise ValidationError('Las opciones no pueden contener solo espacios.')

                opciones = []
                for linea in record.sOpciones.splitlines():
                    if linea.strip():
                        opcion = linea.strip()
                        if opcion in opciones:
                            raise ValidationError('Las opciones de una pregunta no pueden estar repetidas.')
                        opciones.append(opcion)

                if len(opciones) < 2:
                    raise ValidationError('Debes indicar al menos dos opciones.')

    @api.constrains('sOpciones', 'tipo_respuesta_id')
    def _check_respuestas_existentes(self):
        for record in self:
            if record.tipo_respuesta_id.bCon_opciones:
                opciones = []
                for linea in (record.sOpciones or '').splitlines():
                    if linea.strip():
                        opciones.append(linea.strip())
                for respuesta in record.respuesta_ids:
                    if (respuesta.name or '').strip() not in opciones:
                        raise ValidationError('No puedes cambiar las opciones o el tipo porque una respuesta existente dejaría de ser válida.')

    @api.onchange('iNum_pregunta')
    def _onchange_iNum_pregunta(self):
        if self.iNum_pregunta < 1:
            return {
                'value': {'iNum_pregunta': 1},
                'warning': {
                    'title': 'Valor incorrecto',
                    'message': 'El número de pregunta debe ser mayor que 0.'
                }
            }
