# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Idioma(models.Model):
    """Idioma de docencia o requerido.

    Hereda de uprofe.catalogo_mixin (nombre, secuencia, archivado y nº de usos).
    Validaciones (5+):
      1. Nombre no vacío                       (catalogo_mixin)
      2. Nombre único sin distinguir mayúsculas (catalogo_mixin + SQL)
      3. Secuencia no negativa                 (catalogo_mixin)
      4. El nombre solo admite letras, espacios y guiones
      5. El código ISO 639-1 son 2 letras minúsculas y es único (constrains + SQL)
    Reglas de negocio ORM (5+):
      1. create() normaliza el nombre          (catalogo_mixin)
      2. write() normaliza el nombre           (catalogo_mixin)
      3. unlink() impide borrar un idioma en uso (catalogo_mixin)
      4. copy_data() genera un nombre nuevo al duplicar (catalogo_mixin)
      5. Nº de asignaturas, plazas y universidades que lo usan (compute)
      6. onchange del código: lo pasa a minúsculas
    """
    _name = 'uprofe.idioma'
    _inherit = 'uprofe.catalogo_mixin'
    _description = 'Idioma'
    _campos_uso = ('asignatura_destino_ids', 'plaza_erasmus_ids', 'universidad_ids')

    sName = fields.Char(string="Nombre del idioma", size=50, required=True)
    sCodigo = fields.Char(string="Código ISO", size=2, copy=False, help="Código ISO 639-1, por ejemplo 'en'.")

    asignatura_destino_ids = fields.One2many('uprofe.asignatura_destino', 'idioma_id', string="Asignaturas")
    plaza_erasmus_ids = fields.One2many('uprofe.plaza_erasmus', 'idioma_id', string="Plazas")
    # Many2many inversa de uprofe.universidad_destino.idioma_ids (misma tabla de relación)
    universidad_ids = fields.Many2many('uprofe.universidad_destino', 'uprofe_universidad_idioma_rel',
                                       'idioma_id', 'universidad_id', string="Universidades que lo imparten")

    iNum_asignaturas = fields.Integer(string="Nº de asignaturas", compute='_compute_totales')
    iNum_plazas = fields.Integer(string="Nº de plazas", compute='_compute_totales')
    iNum_universidades = fields.Integer(string="Nº de universidades", compute='_compute_totales')

    _sql_constraints = [
        ('nombre_unico', 'UNIQUE("sName")', 'Ya existe un idioma con ese nombre.'),
        ('codigo_unico', 'UNIQUE("sCodigo")', 'Ya existe un idioma con ese código.'),
    ]

    @api.constrains('sName')
    def _check_nombre_format(self):
        regex_nombre = r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'\.\-]+$"
        for record in self:
            if not re.match(regex_nombre, (record.sName or '').strip()):
                raise ValidationError(
                    "El nombre del idioma solo puede contener letras, espacios y guiones."
                )

    @api.constrains('sCodigo')
    def _check_codigo(self):
        for record in self:
            if record.sCodigo and not re.match(r'^[a-z]{2}$', record.sCodigo):
                raise ValidationError("El código del idioma son 2 letras en minúsculas (por ejemplo 'en').")

    @api.depends('asignatura_destino_ids', 'plaza_erasmus_ids', 'universidad_ids')
    def _compute_totales(self):
        for record in self:
            record.iNum_asignaturas = len(record.asignatura_destino_ids)
            record.iNum_plazas = len(record.plaza_erasmus_ids)
            record.iNum_universidades = len(record.universidad_ids)

    @api.onchange('sCodigo')
    def _onchange_codigo(self):
        if self.sCodigo:
            self.sCodigo = self.sCodigo.strip().lower()
