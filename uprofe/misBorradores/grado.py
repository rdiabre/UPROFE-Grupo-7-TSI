# -*- coding: utf-8 -*-
from odoo import models, fields, api

#Un grado dura entre 3 y 6 cursos y tiene entre 180 y 360 créditos
MIN_CURSOS_GRADO = 3
MAX_CURSOS_GRADO = 6
MIN_CREDITOS_GRADO = 180 #grado de tres años
MAX_CREDITOS_GRADO = 360 #doble grado

# Ramas de conocimiento oficiales de la universidad española
RAMAS_CONOCIMIENTO = [
    ('artes_humanidades', 'Artes y Humanidades'),
    ('ciencias', 'Ciencias'),
    ('ciencias_salud', 'Ciencias de la Salud'),
    ('ciencias_sociales', 'Ciencias Sociales y Jurídicas'),
    ('ingenieria_arquitectura', 'Ingeniería y Arquitectura'),
]


class Grado(models.Model):
    _name = 'uprofe.grado'
    _description = 'Grado'
    _order = 'name asc'

    #Herencia por delegación: cada grado es una titulacion y usa sus campos propios.
    #los datos se guardan en la tabla de uprofe.titulacion
    _inherits = {'uprofe.titulacion': 'titulacion_id'}

    titulacion_id = fields.Many2one('uprofe.titulacion', string="Titulación",
                                    required=True, ondelete='cascade')

    #campo propio. Desplegable, así solo admitimos las ramas oficiales sin necesidad de validarlas
    selRama_conocimiento = fields.Selection(RAMAS_CONOCIMIENTO, string="Rama de conocimiento", required=True)

    _sql_constraints = [
        ('titulacion_unique', 'unique(titulacion_id)', 'Esta titulación ya está registrada como grado.'),
    ]

    #reglas sobre los campos heredados.
    #se incluye el id de la titulacion para que la validacion salte también al crear el grado
    @api.constrains('iCreditos_totales', 'iDuracion_cursos', 'titulacion_id')
    def _check_creditos_duracion_grado(self):
        for record in self:
            if not MIN_CREDITOS_GRADO <= record.iCreditos_totales <= MAX_CREDITOS_GRADO:
                raise models.ValidationError(
                    f"Un grado debe tener entre {MIN_CREDITOS_GRADO} y {MAX_CREDITOS_GRADO} créditos.")
            if not MIN_CURSOS_GRADO <= record.iDuracion_cursos <= MAX_CURSOS_GRADO:
                raise models.ValidationError(
                    f"Un grado debe durar entre {MIN_CURSOS_GRADO} y {MAX_CURSOS_GRADO} cursos.")

    #una titulacion es grado o master, nunca ambas
    @api.constrains('titulacion_id')
    def _check_no_es_master(self):
        for record in self:
            if self.env['uprofe.master'].search_count([('titulacion_id', '=', record.titulacion_id.id)]):
                raise models.ValidationError("Esta titulación ya está registrada como máster.")

    #los onchange no se heredan por delegacion, asi que los repetimos aqui
    @api.onchange('sCod_titulacion')
    def _onchange_codigo(self):
        if self.sCod_titulacion:
            self.sCod_titulacion = self.sCod_titulacion.replace(' ', '').upper()

    @api.onchange('name')
    def _onchange_nombre(self):
        if self.name:
            nombre = self.name.strip()
            self.name = nombre[:1].upper() + nombre[1:]