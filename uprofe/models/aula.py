# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Aula(models.Model):
    _name = 'uprofe.aula'
    _description = 'Aula'
    _inherits = {'uprofe.espacio': 'espacio_id'}

    espacio_id = fields.Many2one('uprofe.espacio', required=True)

    # Atributos propios de Aula
    calendario_academico = fields.Char(
        string='Calendario Académico',
        required=True
    )
    tipo_aula = fields.Selection(
        selection=[
            ('docente', 'Aula Docente'),
            ('informatica', 'Aula de Informática'),
            ('seminario', 'Seminario'),
            ('laboratorio', 'Laboratorio')
        ],
        string='Tipo de Aula',
        default='docente',
        required=True
    )

    horario_tutoria_ids = fields.One2many(
        comodel_name='uprofe.horario_tutoria',
        inverse_name='aula_id',
        string='Horarios de Tutoría'
    )
    sesion_ids = fields.One2many(
        comodel_name='uprofe.sesion',
        inverse_name='aula_id',
        string='Sesiones'
    )
    convocatoria_asignatura_ids = fields.One2many(
        comodel_name='uprofe.convocatoria_asignatura',
        inverse_name='aula_id',
        string='Convocatorias de Asignatura'
    )

    TIPOS_ESPACIO = [
        'uprofe.aula',
        'uprofe.laboratorio',
    ]

    @api.constrains('iCapacidad')
    def _check_capacidad(self):
        for record in self:
            if record.capacidad <= 0:
                raise ValidationError('La capacidad debe ser mayor que 0.')

    @api.constrains('sCod_espacio')
    def _check_cod_espacio(self):
        for record in self:
            if not record.sCod_espacio or not record.sCod_espacio.strip():
                raise ValidationError('El código de espacio no puede estar vacío.')
