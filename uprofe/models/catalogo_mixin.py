# -*- coding: utf-8 -*-

import re
import unicodedata

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class CatalogoMixin(models.AbstractModel):
    """Base común de los catálogos (herencia de modelos, Tema 5).

    Lo heredan con _inherit: país, idioma, nivel de estudios, ciudad y los 3 estados.
    Cada catálogo indica en _campos_uso qué relaciones One2many cuentan como "uso".

    Validaciones que aporta a cada catálogo:
      - El nombre no puede estar vacío ni ser solo espacios.
      - El nombre es único sin distinguir mayúsculas (también frente a archivados).
      - La secuencia no puede ser negativa.
    Reglas de negocio (ORM) que aporta a cada catálogo:
      - create(): normaliza el nombre antes de guardar.
      - write(): normaliza el nombre al modificarlo.
      - unlink(): impide borrar un registro en uso (propone archivarlo).
      - copy_data(): al duplicar, genera un nombre nuevo válido.
      - _compute_num_usos(): cuenta cuántos registros lo usan.
    """
    _name = 'uprofe.catalogo_mixin'
    _description = 'Base común de los catálogos'
    _rec_name = 'sName'
    _order = 'iSecuencia, sName'

    # Relaciones One2many que cuentan como uso del registro (la define cada catálogo)
    _campos_uso = ()

    sName = fields.Char(string="Nombre", required=True)
    iSecuencia = fields.Integer(string="Secuencia", default=10,
                                help="Orden en el que aparece en listas y desplegables.")
    active = fields.Boolean(string="Activo", default=True,
                            help="Desmárcalo para archivar el registro sin borrarlo.")
    iNum_usos = fields.Integer(string="Nº de usos", compute='_compute_num_usos')

    # ------------------------------------------------------------------ validaciones
    @api.constrains('sName')
    def _check_nombre_no_vacio(self):
        for record in self:
            if not (record.sName or '').strip():
                raise ValidationError("El nombre no puede estar vacío.")

    @api.constrains('sName')
    def _check_nombre_unico(self):
        for record in self:
            nombre = (record.sName or '').strip().lower()
            candidatos = self.with_context(active_test=False).search([
                ('sName', 'ilike', nombre), ('id', '!=', record.id)])
            if candidatos.filtered(lambda r: (r.sName or '').strip().lower() == nombre):
                raise ValidationError(
                    "Ya existe un registro con el nombre «%s» en %s." % (record.sName, self._description))

    @api.constrains('iSecuencia')
    def _check_secuencia(self):
        for record in self:
            if record.iSecuencia < 0:
                raise ValidationError("La secuencia no puede ser negativa.")

    # ------------------------------------------------------------------ reglas de negocio
    @api.depends(lambda self: self._campos_uso)
    def _compute_num_usos(self):
        for record in self:
            rec = record.with_context(active_test=False)
            record.iNum_usos = sum(len(rec[campo]) for campo in self._campos_uso)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sName'):
                vals['sName'] = self._normalizar_nombre(vals['sName'])
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('sName'):
            vals['sName'] = self._normalizar_nombre(vals['sName'])
        return super().write(vals)

    def unlink(self):
        en_uso = self.filtered(lambda r: r.iNum_usos)
        if en_uso:
            raise UserError(
                "No se puede borrar «%s» porque está en uso. Archívalo en su lugar."
                % ', '.join(en_uso.mapped('sName')))
        return super().unlink()

    def copy_data(self, default=None):
        vals_list = super().copy_data(default=default)
        if not (default and 'sName' in default):
            for record, vals in zip(self, vals_list):
                vals['sName'] = record._nombre_copia(record.sName)
        return vals_list

    # ------------------------------------------------------------------ auxiliares
    @api.model
    def _normalizar_nombre(self, nombre):
        """Quita espacios sobrantes. Los catálogos tipo código lo redefinen."""
        return ' '.join((nombre or '').split())

    def _nombre_copia(self, nombre):
        return '%s copia' % nombre


class EstadoMixin(models.AbstractModel):
    """Base común de los estados de movilidad, learning agreement y línea.

    Hereda de uprofe.catalogo_mixin y añade:
    Validaciones:
      - El nombre va en minúsculas, sin tildes y con guion bajo (p. ej. 'en_curso').
      - El color debe estar entre 0 y 11 (paleta de Odoo).
      - Un estado no puede ser inicial y final a la vez.
      - Solo puede haber un estado inicial.
    Reglas de negocio:
      - El nombre se convierte solo a formato código (minúsculas, sin tildes, '_').
      - Al marcar un estado como inicial se desmarca el anterior (search + write).
      - onchange: si se marca como final deja de ser inicial.
    """
    _name = 'uprofe.estado_mixin'
    _inherit = 'uprofe.catalogo_mixin'
    _description = 'Base común de los estados'

    sName = fields.Char(string="Nombre del estado", size=30, required=True)
    sDescripcion = fields.Text(string="Descripción")
    iColor = fields.Integer(string="Color", default=0)
    bInicial = fields.Boolean(string="Estado inicial", copy=False,
                              help="Estado que se asigna por defecto a los registros nuevos.")
    bFinal = fields.Boolean(string="Estado final",
                            help="Un registro en un estado final ya no puede cambiar de estado.")

    @api.constrains('sName')
    def _check_nombre_format(self):
        for record in self:
            if not re.match(r'^[a-z]+(_[a-z]+)*$', (record.sName or '').strip()):
                raise ValidationError(
                    "El nombre del estado va en minúsculas, sin tildes ni espacios "
                    "(usad guion bajo para separar palabras, por ejemplo 'en_curso').")

    @api.constrains('iColor')
    def _check_color(self):
        for record in self:
            if not 0 <= record.iColor <= 11:
                raise ValidationError("El color debe ser un número entre 0 y 11.")

    @api.constrains('bInicial', 'bFinal')
    def _check_inicial_final(self):
        for record in self:
            if record.bInicial and record.bFinal:
                raise ValidationError("Un estado no puede ser inicial y final a la vez.")

    @api.constrains('bInicial')
    def _check_un_solo_inicial(self):
        if self.search_count([('bInicial', '=', True)]) > 1:
            raise ValidationError("Solo puede haber un estado inicial.")

    @api.onchange('bFinal')
    def _onchange_final(self):
        if self.bFinal:
            self.bInicial = False

    @api.model_create_multi
    def create(self, vals_list):
        if any(vals.get('bInicial') for vals in vals_list):
            self.search([('bInicial', '=', True)]).write({'bInicial': False})
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('bInicial'):
            (self.search([('bInicial', '=', True)]) - self).write({'bInicial': False})
        return super().write(vals)

    @api.model
    def _normalizar_nombre(self, nombre):
        """'En curso ' -> 'en_curso' (minúsculas, sin tildes, guion bajo)."""
        nombre = unicodedata.normalize('NFKD', nombre or '')
        nombre = ''.join(c for c in nombre if not unicodedata.combining(c))
        return re.sub(r'[\s\-]+', '_', nombre.strip().lower())

    def _nombre_copia(self, nombre):
        return '%s_copia' % nombre

    @api.model
    def _estado_inicial(self):
        return self.search([('bInicial', '=', True)], limit=1)
