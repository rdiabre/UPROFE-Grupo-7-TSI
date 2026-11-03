# -*- coding: utf-8 -*-
from odoo import models, fields

class Pregunta(models.Model):
    _name = 'uprofe.pregunta'
    _description = 'Pregunta de Encuesta'

    name = fields.Char(string='Enunciado de la Pregunta', required=True)
    num_pregunta = fields.Integer(string='Número de Pregunta', required=True, default=1)

    # Relación Many2one con la entidad TipoRespuesta (que irá en su propia rama/issue)
    tipo_respuesta_id = fields.Many2one(
        'uprofe.tipo_respuesta', 
        string='Tipo de Respuesta'
    )

    # Relación Many2one con Encuesta
    encuesta_id = fields.Many2one(
        'uprofe.encuesta', 
        string='Encuesta', 
        ondelete='cascade'
    )