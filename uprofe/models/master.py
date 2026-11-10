# -*- coding: utf-8 -*-
from odoo import models, fields, api

#Un máster dura entre 1 y 2 cursos y tiene entre 60 y 120 créditos
MIN_CURSOS_MASTER = 1
MAX_CURSOS_MASTER = 2
MIN_CREDITOS_MASTER = 60
MAX_CREDITOS_MASTER = 120

#Orientaciones de un máster
ORIENTACIONES = [
    ('academica', 'Académica'),
    ('profesional', 'Profesional'),
    ('investigacion', 'Investigación'),
]

#se aplican conceptos muy similares a los que he usado en el modelo de grado
class Master(models.Model):
    _name = 'uprofe.master'
    _description = 'Máster'
    _order = 'name asc'

    _inherits = {'uprofe.titulacion': 'titulacion_id'}

    titulacion_id = fields.Many2one('uprofe.titulacion', string="Titulación",
                                    required=True, ondelete='cascade')

    selOrientacion = fields.Selection(ORIENTACIONES, string="Orientación", required=True)

    _sql_constraints = [
        ('titulacion_unique', 'unique(titulacion_id)', 'Esta titulación ya está registrada como máster.'),
    ]

    @api.constrains('iCreditos_totales', 'iDuracion_cursos', 'titulacion_id')
    def _check_creditos_duracion_master(self):
        for record in self:
            if not MIN_CREDITOS_MASTER <= record.iCreditos_totales <= MAX_CREDITOS_MASTER:
                raise models.ValidationError(
                    f"Un máster debe tener entre {MIN_CREDITOS_MASTER} y {MAX_CREDITOS_MASTER} créditos.")
            if not MIN_CURSOS_MASTER <= record.iDuracion_cursos <= MAX_CURSOS_MASTER:
                raise models.ValidationError(
                    f"Un máster debe durar entre {MIN_CURSOS_MASTER} y {MAX_CURSOS_MASTER} cursos.")

    @api.constrains('titulacion_id')
    def _check_no_es_grado(self):
        for record in self:
            if self.env['uprofe.grado'].search_count([('titulacion_id', '=', record.titulacion_id.id)]):
                raise models.ValidationError("Esta titulación ya está registrada como grado.")

    @api.onchange('sCod_titulacion')
    def _onchange_codigo(self):
        if self.sCod_titulacion:
            self.sCod_titulacion = self.sCod_titulacion.replace(' ', '').upper()

    @api.onchange('name')
    def _onchange_nombre(self):
        if self.name:
            nombre = self.name.strip()
            self.name = nombre[:1].upper() + nombre[1:]