# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TipoRespuesta(models.Model):
    _name = 'uprofe.tipo_respuesta'
    _description = 'Tipo de respuesta'
    _order = 'name asc'

    name = fields.Char(string='Tipo', required=True)
    bCon_opciones = fields.Boolean(string='Requiere opciones', default=False )

    pregunta_ids = fields.One2many('uprofe.pregunta', 'tipo_respuesta_id', string='Preguntas')

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            if record.name:
                lDominio = [
                    ('id', '!=', record.id),
                    ('name', '=ilike', record.name.strip())
                ]

                if self.search_count(lDominio):
                    raise ValidationError('Ya existe un tipo de respuesta con ese nombre.')

    @api.constrains('name')
    def _check_name_not_empty(self):
        for record in self:
            nombre = (record.name or '').strip()

            if not nombre:
                raise ValidationError('El nombre del tipo de respuesta no puede estar vacío.')
            if record.name != nombre:
                raise ValidationError('El nombre del tipo de respuesta no puede tener espacios al principio o al final.' )
            if len(nombre) > 50:
                raise ValidationError( 'El nombre del tipo de respuesta no puede superar los 50 caracteres.')


    @api.constrains('bCon_opciones')
    def _check_preguntas_con_opciones(self):
        for record in self:
            if record.bCon_opciones:
                for pregunta in record.pregunta_ids:
                    opciones = []
                    for linea in (pregunta.sOpciones or '').splitlines():
                        if linea.strip():
                            opcion = linea.strip()
                            if opcion in opciones:
                                raise ValidationError('Una pregunta de este tipo tiene opciones repetidas.')
                            opciones.append(opcion)
                    if len(opciones) < 2:
                        raise ValidationError('Todas las preguntas de este tipo deben tener al menos dos opciones distintas.')
                    for respuesta in pregunta.respuesta_ids:
                        if (respuesta.name or '').strip() not in opciones:
                            raise ValidationError('No puedes activar las opciones porque una respuesta existente dejaría de ser válida.')
