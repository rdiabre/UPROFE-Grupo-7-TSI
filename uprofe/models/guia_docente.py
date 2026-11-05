# -*- coding: utf-8 -*-
from odoo import models, fields, api

class GuiaDocente(models.Model):
    _name = 'uprofe.guia_docente'
    _description = 'UPROFE Guía docente'
    _order = 'curso_academico desc, asignatura_id'

    # Una guía describe una asignatura (1,1)
    # Si se borra la asignatura, se borran sus guías (ondelete='cascade')
    
    # PK = (asignatura_id, curso_academico)
    asignatura_id = fields.Many2one('uprofe.asignatura', string="Asignatura", required=True, ondelete='cascade')

    curso_academico = fields.Char(string="Curso académico", required=True, help="Con el formato 2026/2027")
    fichero = fields.Binary(string="Fichero", required=True, help="Guía docente en PDF")
    # Odoo lo necesita para guardar el nombre del fichero al subirlo
    nombre_fichero = fields.Char(string="Nombre del fichero")

    # Campo calculado (no se guarda): indica si la guía es la del curso académico actual
    es_actual = fields.Boolean(string="Curso actual", compute='_compute_es_actual')

    # Solo puede haber una guía por asignatura y curso académico
    _sql_constraints = [
        ('asignatura_curso_unique', 'unique(asignatura_id, curso_academico)',
         'Esta asignatura ya tiene una guía docente para ese curso académico.'),
    ]

    