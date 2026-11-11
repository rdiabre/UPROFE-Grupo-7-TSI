# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class convocatoria(models.Model):
    _name = 'uprofe.convocatoria'
    _description = 'Convocatoria'
    _order = 'dtFechaApertura desc'
    _rec_name = 'sName'

    sName = fields.Char(string="Código de la convocatoria", size=50, required=True)
    sCursoAcademico = fields.Char(string="Curso académico", size=9, required=True)
    dtFechaApertura = fields.Date(string="Fecha de apertura", required=True)
    dtFechaCierre = fields.Date(string="Fecha de cierre", required=True)

    oTipoConvocatoriaId = fields.Many2one('uprofe.tipo_convocatoria', string="Tipo de convocatoria", required=True)
    oEstadoConvocatoriaId = fields.Many2one('uprofe.estado_convocatoria', string="Estado", required=True)
    
    @api.constrains('sName')
    def _check_name_unique(self):
        for record in self:
            if self.search_count([("id", "!=", record.id), ("sName", "=ilike", record.sName.strip())]):
                raise ValidationError("Ya existe una convocatoria con este código.")

    @api.constrains('sName')
    def _check_name_not_empty(self):
        for record in self:
            if len(record.sName.strip()) == 0:
                raise ValidationError("El código de la convocatoria no puede estar vacío.")

    @api.constrains('sCursoAcademico')
    def _check_curso_not_empty(self):
        for record in self:
            if len(record.sCursoAcademico.strip()) == 0:
                raise ValidationError("El curso académico no puede estar vacío.")

    @api.constrains('dtFechaApertura', 'dtFechaCierre')
    def _check_fechas(self):
        for record in self:
            if record.dtFechaCierre < record.dtFechaApertura    :
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