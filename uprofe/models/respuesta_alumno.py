# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RespuestaAlumno(models.Model):
    _name = 'uprofe.respuesta_alumno'
    _description = 'Respuesta de un alumno a una pregunta'
    _rec_name = 'pregunta_id'

    pregunta_id = fields.Many2one('uprofe.pregunta', string='Pregunta',
                                  required=True, ondelete='cascade')
    sTexto_respuesta = fields.Text(string='Respuesta', required=True)

    # Descomento cuando uprofe.alumno esté en main
    # alumno_id = fields.Many2one('uprofe.alumno', string='Alumno',
    #                             required=True, ondelete='cascade')
    # _sql_constraints = [
    #     ('pregunta_alumno_uniq', 'unique(pregunta_id, alumno_id)',
    #      'Este alumno ya ha respondido a esta pregunta.'),
    # ]

    @api.constrains('pregunta_id', 'sTexto_respuesta')
    def _check_respuesta_valida(self):
        for record in self:
            respuesta = (record.sTexto_respuesta or '').strip()
            if not respuesta:
                raise ValidationError("La respuesta no puede estar vacía.")
            if record.pregunta_id.bconopciones:
                opciones = [l.strip() for l in (record.pregunta_id.sopciones or '').splitlines()
                            if l.strip()]
                if respuesta not in opciones:
                    raise ValidationError(
                        "La respuesta debe ser una de las opciones de la pregunta.")