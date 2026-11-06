# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api

# La UPO se creó en 1997
FECHA_MINIMA = date(1997, 1, 1)

class Expediente(models.Model):
    _name = 'uprofe.expediente'
    _description = 'UPROFE Expediente académico'
    _order = 'iNum_expediente desc'
    # En los desplegables se puede buscar el expediente por el nombre o el DNI del alumno
    _rec_names_search = ['alumno_id', 'sAlumno_dni']

    # PK
    iNum_expediente = fields.Integer(string="Número de expediente", required=True, copy=False, default=lambda self: self._siguiente_numero())
    dFecha_apertura = fields.Date(string="Fecha de apertura", required=True, default=fields.Date.context_today)

    # Relaciones del diagrama E-R
    # Un expediente es de un alumno (1,1) y de una titulación (1,1)
    alumno_id = fields.Many2one('uprofe.alumno', string="Alumno", required=True, ondelete='restrict')
    titulacion_id = fields.Many2one('uprofe.titulacion', string="Titulación", required=True, ondelete='restrict')
    # Asignaturas registradas en el expediente (superadas): N a M con Asignatura
    asignatura_ids = fields.Many2many('uprofe.asignatura', 'uprofe_asignatura_expediente_rel', 'expediente_id', 'asignatura_id', string="Asignaturas superadas")

    # Atributos derivados del diagrama E-R
    fCreditos_superados = fields.Float(string="Créditos superados", compute='_compute_creditos_superados', store=True)
    # La nota media se calculará con las notas de las actas (en el PR de Acta y Línea de acta)
    fNota_media = fields.Float(string="Nota media", readonly=True, digits=(4, 2), aggregator='avg')

    # Auxiliares calculados
    iNum_asignaturas = fields.Integer(string="Nº de asignaturas superadas", compute='_compute_creditos_superados', store=True)
    # (Alumno hereda sDni de Persona)
    sAlumno_dni = fields.Char(string="DNI del alumno", related='alumno_id.sDni')

    _sql_constraints = [
        ('num_expediente_unique', 'unique("iNum_expediente")', 'Ya existe un expediente con este número.'),
        # Un alumno solo tiene un expediente por titulación
        ('alumno_titulacion_unique', 'unique(alumno_id, titulacion_id)',
         'Este alumno ya tiene un expediente en esta titulación.'),
    ]

    # Número de expediente: el siguiente al último que existe
    def _siguiente_numero(self):
        ultimo = self.search([], order='iNum_expediente desc', limit=1)
        return ultimo.iNum_expediente + 1 if ultimo else 1

    # Nombre que se muestra: "Exp. 00012 – Osito Gominola"
    @api.depends('iNum_expediente', 'alumno_id')
    def _compute_display_name(self):
        for record in self:
            alumno = f"{record.alumno_id.name or ''} {record.alumno_id.sApellidos or ''}".strip()
            record.display_name = f"Exp. {record.iNum_expediente:05d} - {alumno}"

    # Suma de los créditos de las asignaturas superadas
    @api.depends('asignatura_ids', 'asignatura_ids.fCreditos')
    def _compute_creditos_superados(self):
        for record in self:
            record.fCreditos_superados = sum(record.asignatura_ids.mapped('fCreditos'))
            record.iNum_asignaturas = len(record.asignatura_ids)

    # Número de expediente mayor que 0
    @api.constrains('iNum_expediente')
    def _check_num_expediente(self):
        for record in self:
            if record.iNum_expediente <= 0:
                raise models.ValidationError("El número de expediente debe ser mayor que 0.")

    # No puede ser futura
    @api.constrains('dFecha_apertura')
    def _check_fecha_apertura_futura(self):
        hoy = fields.Date.context_today(self)
        for record in self:
            if record.dFecha_apertura > hoy:
                raise models.ValidationError("La fecha de apertura no puede ser posterior a hoy.")

    # No puede ser anterior a la creación de la universidad
    @api.constrains('dFecha_apertura')
    def _check_fecha_apertura_minima(self):
        for record in self:
            if record.dFecha_apertura < FECHA_MINIMA:
                raise models.ValidationError("La fecha de apertura no puede ser anterior a 1997, "
                                      "año de creación de la Universidad Pablo de Olavide.")

    # Nota media entre 0 y 10
    @api.constrains('fNota_media')
    def _check_nota_media(self):
        for record in self:
            if not 0 <= record.fNota_media <= 10:
                raise models.ValidationError("La nota media debe estar entre 0 y 10.")
