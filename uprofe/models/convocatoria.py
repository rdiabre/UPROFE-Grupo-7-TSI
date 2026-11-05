# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class convocatoria(models.Model):
    _name = 'uprofe.convocatoria'
    _description = 'Convocatoria'
    _order= 'fecha_apertura desc'
    
    name = fields.Char(string="Código de la convocatoria", size=50, required=True)
    curso_academico = fields.Char(string="Curso académico", size=9, required=True)
    fecha_apertura = fields.Date(string="Fecha de apertura", required=True)
    fecha_cierre = fields.Date(string="Fecha de cierre", required=True)

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

    @api.constrains('curso_academico')
    def _check_curso_not_empty(self):
        for record in self:
            if len(record.curso_academico.strip()) == 0:
                raise ValidationError("El curso académico no puede estar vacío.")

    @api.constrains('fecha_apertura', 'fecha_cierre')
    def _check_fechas(self):
        for record in self:
            if record.fecha_cierre < record.fecha_apertura:
                raise ValidationError("La fecha de cierre no puede ser anterior a la de apertura.")

    def write(self, vals):
        self._strip_string_values(vals)
        return super().write(vals)

    def _strip_string_values(self, vals):
        for field_name, val in vals.items():
            if isinstance(val, str):
                field = self._fields.get(field_name)
                if field and field.type in ('char', 'text'):
                    vals[field_name] = val.strip()
        return vals