# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RespuestaAlumno(models.Model):
    _name = 'uprofe.respuesta_alumno'
    _description = 'Respuesta de un alumno a una pregunta'

    name = fields.Text(string='Respuesta', required=True)
   
    pregunta_id = fields.Many2one('uprofe.pregunta', string='Pregunta', required=True)
    encuesta_id = fields.Many2one(related='pregunta_id.encuesta_id', string='Encuesta', store=True)
    sOpciones = fields.Text(related='pregunta_id.sOpciones', string='Opciones disponibles')
    bCon_opciones = fields.Boolean(related='pregunta_id.tipo_respuesta_id.bCon_opciones', string='Requiere opciones')

    # Descomentar cuando exista el modelo uprofe.alumno
    # alumno_id = fields.Many2one('uprofe.alumno', string='Alumno', required=True)

    # Descomentar junto con alumno_id
    # _sql_constraints = [
    #     ('pregunta_alumno_uniq', 'unique(pregunta_id, alumno_id)', 'Este alumno ya ha respondido a esta pregunta.'),
    # ]

    @api.constrains('pregunta_id', 'name')
    def _check_respuesta_valida(self):
        for record in self:
            respuesta = (record.name or '').strip()

            if not respuesta:
                raise ValidationError('La respuesta no puede estar vacía.')
            if record.pregunta_id.tipo_respuesta_id.bCon_opciones:
                opciones = []
                for linea in (record.pregunta_id.sOpciones or '').splitlines():
                    if linea.strip():
                        opciones.append(linea.strip())
                if respuesta not in opciones:
                    raise ValidationError('La respuesta debe ser una de las opciones de la pregunta.')

    @api.onchange('pregunta_id', 'name')
    def _onchange_respuesta(self):
        if self.pregunta_id and self.name:
            if self.pregunta_id.tipo_respuesta_id.bCon_opciones:
                opciones = []
                for linea in (self.pregunta_id.sOpciones or '').splitlines():
                    if linea.strip():
                        opciones.append(linea.strip())
                if self.name.strip() not in opciones:
                    return {
                        'value': {'name': False},
                        'warning': {
                            'title': 'Respuesta no válida',
                            'message': 'Escribe exactamente una de las opciones disponibles.'
                        }
                    }
