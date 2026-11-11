# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Encuesta(models.Model):
    _name = 'uprofe.encuesta'
    _description = 'Encuesta de satisfacción docente'
    _order = 'dtFecha_inicio desc'

    sCod_encuesta = fields.Char(string='Código', required=True, help='Por ejemplo: ENC-2026-01')
    name = fields.Char(string='Nombre', required=True)
    sDescripcion = fields.Text(string='Descripción')
    sCurso_academico = fields.Char(string='Curso académico', required=True, help='Formato AAAA/AAAA. Por ejemplo: 2026/2027')
    dtFecha_inicio = fields.Date(string='Fecha de inicio', required=True)
    dtFecha_fin = fields.Date(string='Fecha de fin', required=True)

    asignatura_id = fields.Many2one('uprofe.asignatura', string='Asignatura')
    profesor_id = fields.Many2one('uprofe.profesor', string='Profesor revisor', required=True)
    pregunta_ids = fields.One2many('uprofe.pregunta', 'encuesta_id', string='Preguntas')

    @api.constrains('sCod_encuesta')
    def _check_codigo(self):
        for record in self:
            codigo = (record.sCod_encuesta or '').strip()
            if not codigo:
                raise ValidationError('El código de la encuesta no puede estar vacío.')
            if record.sCod_encuesta != codigo:
                raise ValidationError('El código de la encuesta no puede tener espacios al principio o al final.')
            if self.search_count([
                ('id', '!=', record.id),
                ('sCod_encuesta', '=ilike', codigo)
            ]):
                raise ValidationError('Ya existe una encuesta con ese código.')

    @api.constrains('name')
    def _check_nombre(self):
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError('El nombre de la encuesta no puede estar vacío.')

    @api.constrains('sCurso_academico')
    def _check_curso_academico(self):
        for record in self:
            curso = record.sCurso_academico or ''
            if len(curso) != 9:
                raise ValidationError('El curso académico debe tener el formato AAAA/AAAA.')
            if curso[4] != '/':
                raise ValidationError('Los años del curso académico deben estar separados por /.')

            primer_anio = curso[:4] 
            segundo_anio = curso[5:]

            for caracter in primer_anio + segundo_anio:
                if caracter not in '0123456789':
                    raise ValidationError('Los años del curso académico deben contener únicamente números.')

            if int(segundo_anio) != int(primer_anio) + 1:
                raise ValidationError('Los años del curso académico deben ser consecutivos. Por ejemplo: 2026/2027.')

    @api.constrains('dtFecha_inicio', 'dtFecha_fin')
    def _check_fechas(self):
        for record in self:
            if record.dtFecha_inicio and record.dtFecha_fin:
                if record.dtFecha_fin < record.dtFecha_inicio:
                    raise ValidationError('La fecha de fin no puede ser anterior a la fecha de inicio.')

    @api.constrains('pregunta_ids')
    def _check_preguntas(self):
        for record in self:
            if not record.pregunta_ids:
                raise ValidationError('Una encuesta debe tener al menos una pregunta.')

    @api.onchange('dtFecha_inicio', 'dtFecha_fin')
    def _onchange_fechas(self):
        if self.dtFecha_inicio and self.dtFecha_fin:
            if self.dtFecha_fin < self.dtFecha_inicio:
                return {
                    'value': {'dtFecha_fin': self.dtFecha_inicio},
                    'warning': {
                        'title': 'Fechas incorrectas',
                        'message': 'La fecha de fin no puede ser anterior a la fecha de inicio.'
                    }
                }
