# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api

MAX_CODIGO = 10
MAX_NOMBRE = 60
MAX_CURSO = 6             # un grado tiene 4 cursos, a veces hasta 6
MAX_CREDITOS = 30         # el TFG puede tener más de 6
HORAS_POR_CREDITO = 25    # 1 crédito ECTS equivale a 25-30 horas de trabajo del alumno
REGEX_CODIGO = r'^[A-Z0-9]+$'  # letras mayúsculas y números, sin espacios. Ej: 702023


class Asignatura(models.Model):
    _name = 'uprofe.asignatura'
    _description = 'UPROFE Asignatura'
    _order = 'curso asc, cuatrimestre asc, name asc'

    # En los desplegables de otros modelos (Sesión, Guía docente...) se puede
    # buscar la asignatura escribiendo su nombre o su código
    _rec_names_search = ['name', 'cod_asig']

    cod_asig = fields.Char(string="Código", required=True, help="Código de la asignatura. Por ejemplo: 702023") # PK
    name = fields.Char(string="Nombre", required=True)
    curso = fields.Integer(string="Curso", required=True, default=1)
    cuatrimestre = fields.Selection([('1', 'Primer cuatrimestre'),
                                     ('2', 'Segundo cuatrimestre'),
                                     ('anual', 'Anual')],
                                    string="Cuatrimestre", required=True, default='1')
    creditos = fields.Float(string="Créditos ECTS", required=True, default=6.0)
    limite_faltas = fields.Integer(string="Límite de faltas", default=0,
                                   help="Número máximo de faltas de asistencia permitidas")

    # Campo calculado (no se guarda) para llegar a las 5 reglas de negocio: horas de trabajo que supone la asignatura para el alumno
    horas_trabajo = fields.Float(string="Horas de trabajo del alumno", compute='_compute_horas_trabajo',
                                 help=f"Créditos ECTS x {HORAS_POR_CREDITO} horas")

    