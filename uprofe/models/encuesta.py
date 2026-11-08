# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError

# Curso académico formato AAAA/AAAA ej 2026/2027
REGEX_CURSO = r'^(\d{4})/(\d{4})$'


class Encuesta(models.Model):
    _name = 'uprofe.encuesta'
    _description = 'Encuesta de satisfacción docente'
    _order = 'dtFecha_inicio desc'

    sCod_encuesta = fields.Char(string='Código', required=True,
                                help='Código de la encuesta. Por ejemplo: ENC-2026-01')  # PK
    name = fields.Char(string='Nombre', required=True)
    sDescripcion = fields.Text(string='Descripción')
    sCurso_academico = fields.Char(string='Curso académico', required=True,
                                   help='Formato AAAA/AAAA. Por ejemplo: 2026/2027')
    dtFecha_inicio = fields.Date(string='Fecha de inicio', required=True,
                                 default=fields.Date.context_today)
    dtFecha_fin = fields.Date(string='Fecha de fin', required=True)

    pregunta_ids = fields.One2many('uprofe.pregunta', 'encuesta_id', string='Preguntas')

    # Descomento cuando uprofe.asignatura esté en main
    # trata sobre (0,1): una encuesta trata sobre como mucho una asignatura
    # asignatura_id = fields.Many2one('uprofe.asignatura', string='Asignatura',
    #                                 ondelete='set null')

    # Descomento cuando uprofe.profesor esté en main
    # revisa (1,1): cada encuesta la revisa exactamente un profesor
    # profesor_id = fields.Many2one('uprofe.profesor', string='Profesor revisor',
    #                               required=True, ondelete='restrict')

    # constrains
    @api.constrains('sCod_encuesta')
    def _check_cod_unico(self):
        for record in self:
            cod = (record.sCod_encuesta or '').strip()
            if not cod:
                raise ValidationError("El código de la encuesta no puede estar vacío.")
            if self.search_count([('id', '!=', record.id), ('sCod_encuesta', '=ilike', cod)]):
                raise ValidationError("Ya existe una encuesta con ese código.")

    @api.constrains('sCurso_academico')
    def _check_curso_academico(self):
        for record in self:
            m = re.match(REGEX_CURSO, (record.sCurso_academico or '').strip())
            if not m or int(m.group(2)) != int(m.group(1)) + 1:
                raise ValidationError(
                    "El curso académico debe tener el formato AAAA/AAAA con años consecutivos. "
                    "Por ejemplo: 2026/2027.")

    @api.constrains('dtFecha_inicio', 'dtFecha_fin')
    def _check_fechas(self):
        for record in self:
            if record.dtFecha_inicio and record.dtFecha_fin \
                    and record.dtFecha_fin < record.dtFecha_inicio:
                raise ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")

    @api.constrains('pregunta_ids')
    def _check_preguntas(self):
        for record in self:
            if not record.pregunta_ids:
                raise ValidationError("Una encuesta debe tener al menos una pregunta.")

    # onchange
    @api.onchange('dtFecha_inicio', 'dtFecha_fin')
    def _onchange_fechas(self):
        if self.dtFecha_inicio and self.dtFecha_fin and self.dtFecha_fin < self.dtFecha_inicio:
            return {
                'value': {'dtFecha_fin': self.dtFecha_inicio},
                'warning': {
                    'title': 'Fechas incorrectas',
                    'message': 'La fecha de fin no puede ser anterior a la fecha de inicio.'
                }
            }