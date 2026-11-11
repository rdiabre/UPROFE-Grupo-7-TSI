# -*- coding: utf-8 -*-
# Autor: Isabel Cherino

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

SEMESTRES = [('1', 'Primer semestre'), ('2', 'Segundo semestre'), ('anual', 'Anual')]


class AsignaturaDestino(models.Model):
    """Asignatura que se cursa en la universidad de destino.

    Validaciones (5+):
      1. Los créditos ECTS son mayores que 0
      2. Los créditos ECTS no superan 30 y van de 0,5 en 0,5
      3. El idioma de impartición lo imparte la universidad (Many2many idioma_ids)
      4. El código solo admite mayúsculas, números y guiones (+ SQL único)
      5. El nombre tiene al menos 3 caracteres
    Reglas de negocio ORM (5+):
      1. Nº de líneas de learning agreement que la usan (compute)
      2. Créditos reconocidos en total con esta asignatura (compute con mapped)
      3. create() pasa el código a mayúsculas
      4. write() pasa el código a mayúsculas
      5. onchange de la universidad: propone un idioma que esa universidad imparte
      6. unlink() impide borrar una asignatura usada en learning agreements
      7. Nombre a mostrar «código · nombre» (_compute_display_name)
    """
    _name = 'uprofe.asignatura_destino'
    _description = 'Asignatura de la universidad de destino'
    _rec_name = 'sName'
    _order = 'cod_asig_destino'

    cod_asig_destino = fields.Char(string="Código de la asignatura", size=30, required=True)
    sName = fields.Char(string="Nombre", size=150, required=True)
    fCreditos_ects = fields.Float(string="Créditos ECTS", required=True)
    sSemestre = fields.Selection(SEMESTRES, string="Semestre", default='1')
    sDescripcion = fields.Text(string="Descripción")

    universidad_id = fields.Many2one(
       'uprofe.universidad_destino',
       string="Universidad de destino",
       required=True,
       ondelete='restrict',
    )

    idioma_id = fields.Many2one(
       'uprofe.idioma',
       string="Idioma de impartición",
       required=True,
       ondelete='restrict',
    )

    linea_ids = fields.One2many('uprofe.la_linea', 'asignatura_destino_id', string="Líneas de acuerdo")
    iNum_lineas = fields.Integer(string="Nº de líneas", compute='_compute_lineas', store=True)
    fCreditos_reconocidos = fields.Float(string="Créditos reconocidos", compute='_compute_lineas', store=True)

    _sql_constraints = [
        ('cod_asig_destino_unico', 'UNIQUE(cod_asig_destino)',
         'Ya existe una asignatura de destino con ese código.'),
    ]

    # ------------------------------------------------------------------ validaciones
    @api.constrains('fCreditos_ects')
    def _check_creditos_ects(self):
        for record in self:
            if record.fCreditos_ects <= 0:
                raise ValidationError("Los créditos ECTS deben ser mayores que 0.")

    @api.constrains('fCreditos_ects')
    def _check_creditos_formato(self):
        for record in self:
            if record.fCreditos_ects > 30 or (record.fCreditos_ects * 2) % 1:
                raise ValidationError("Los créditos ECTS no pueden superar 30 y van de 0,5 en 0,5.")

    @api.constrains('idioma_id', 'universidad_id')
    def _check_idioma_universidad(self):
        for record in self:
            if record.idioma_id not in record.universidad_id.idioma_ids:
                raise ValidationError("%s no imparte docencia en %s."
                                      % (record.universidad_id.sName, record.idioma_id.sName))

    @api.constrains('cod_asig_destino')
    def _check_codigo(self):
        for record in self:
            if not re.match(r'^[A-Z0-9]+(-[A-Z0-9]+)*$', record.cod_asig_destino or ''):
                raise ValidationError("El código solo admite mayúsculas, números y guiones (por ejemplo ROM-INF-101).")

    @api.constrains('sName')
    def _check_nombre(self):
        for record in self:
            if len((record.sName or '').strip()) < 3:
                raise ValidationError("El nombre de la asignatura debe tener al menos 3 caracteres.")

    # ------------------------------------------------------------------ reglas de negocio
    @api.depends('linea_ids', 'linea_ids.fCreditos_reconocidos')
    def _compute_lineas(self):
        for record in self:
            record.iNum_lineas = len(record.linea_ids)
            record.fCreditos_reconocidos = sum(record.linea_ids.mapped('fCreditos_reconocidos'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('cod_asig_destino'):
                vals['cod_asig_destino'] = vals['cod_asig_destino'].strip().upper()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('cod_asig_destino'):
            vals['cod_asig_destino'] = vals['cod_asig_destino'].strip().upper()
        return super().write(vals)

    @api.onchange('universidad_id')
    def _onchange_universidad(self):
        idiomas = self.universidad_id.idioma_ids
        if idiomas and self.idioma_id not in idiomas:
            self.idioma_id = idiomas[:1]

    def unlink(self):
        usadas = self.filtered('linea_ids')
        if usadas:
            raise UserError("No se puede borrar %s porque se usa en learning agreements."
                            % ', '.join(usadas.mapped('sName')))
        return super().unlink()

    @api.depends('cod_asig_destino', 'sName')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "%s · %s" % (record.cod_asig_destino or '', record.sName or '')
