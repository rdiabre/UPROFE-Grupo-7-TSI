# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Aula(models.Model):
    _name = 'uprofe.aula'
    _inherit = 'uprofe.espacio'
    _description = 'Aula'
    _rec_name = 'cod_espacio'

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
