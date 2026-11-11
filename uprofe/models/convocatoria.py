# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class convocatoria(models.Model):
    _name = 'uprofe.convocatoria'
    _description = 'Convocatoria'
    _order = 'dtFechaApertura desc'
    _rec_name = 'name'

    name = fields.Char(string="Código de la convocatoria", size=50, required=True)
    sCursoAcademico = fields.Char(string="Curso académico", size=9, required=True)
    dtFechaApertura = fields.Date(string="Fecha de apertura", required=True)
    dtFechaCierre = fields.Date(string="Fecha de cierre", required=True)

    tipo_convocatoria_id = fields.Many2one('uprofe.tipo_convocatoria', string="Tipo de convocatoria", required=True)
    estado_convocatoria_id = fields.Many2one('uprofe.estado_convocatoria', string="Estado", required=True)

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("name", "=ilike", record.name.strip())]):
                raise ValidationError("Ya existe una convocatoria con este código.")

    @api.constrains('name')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.name.strip()) == 0:
                raise ValidationError("El código de la convocatoria no puede estar vacío.")

    @api.constrains('sCursoAcademico')
    def _check_curso_not_empty(self):
        for record in self:
            if len(record.sCursoAcademico.strip()) == 0:
                raise ValidationError("El curso académico no puede estar vacío.")

    @api.constrains('dtFechaApertura', 'dtFechaCierre')
    def _check_fechas(self):
        for record in self:
            if record.dtFechaCierre < record.dtFechaApertura:
                raise ValidationError("La fecha de cierre no puede ser anterior a la de apertura.")
