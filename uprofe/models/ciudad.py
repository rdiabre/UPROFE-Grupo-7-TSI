# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Ciudad(models.Model):
    """Ciudad donde está una universidad de destino.

    Hereda de uprofe.catalogo_mixin (nombre, secuencia, archivado y nº de usos).
    Validaciones (5+):
      1. Nombre no vacío                       (catalogo_mixin)
      2. Secuencia no negativa                 (catalogo_mixin)
      3. El nombre solo admite letras, espacios y guiones
      4. Nombre único dentro de su país (redefine la del mixin, + SQL)
      5. La población no puede ser negativa
      6. Solo puede haber una capital por país
    Reglas de negocio ORM (5+):
      1. create() normaliza el nombre          (catalogo_mixin)
      2. write() normaliza el nombre           (catalogo_mixin)
      3. unlink() impide borrar una ciudad con universidades (catalogo_mixin)
      4. copy_data() genera un nombre nuevo al duplicar (catalogo_mixin)
      5. Nombre a mostrar «Ciudad (País)» (_compute_display_name)
      6. onchange: avisa si el país ya tiene capital
    """
    _name = 'uprofe.ciudad'
    _inherit = 'uprofe.catalogo_mixin'
    _description = 'Ciudad'
    _campos_uso = ('universidad_ids',)

    sName = fields.Char(string="Nombre de la ciudad", size=50, required=True)
    sDescription = fields.Char(string="Descripción de la ciudad", size=150)
    iPoblacion = fields.Integer(string="Población (habitantes)")
    bCapital = fields.Boolean(string="Es la capital")

    pais_id = fields.Many2one(
       'uprofe.pais',
       string="País",
       required=True,
       ondelete='cascade',
    )
    universidad_ids = fields.One2many('uprofe.universidad_destino', 'ciudad_id', string="Universidades")

    _sql_constraints = [
       ('ciudad_unica_por_pais', 'UNIQUE("sName", pais_id)',
        'Ya existe una ciudad con ese nombre en ese país.'),
    ]

    @api.constrains('sName')
    def _check_nombre_format(self):
        regex_nombre = r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'\.\-]+$"
        for record in self:
            if not re.match(regex_nombre, (record.sName or '').strip()):
                raise ValidationError(
                    "El nombre de la ciudad solo puede contener letras, espacios y guiones."
                )

    @api.constrains('sName', 'pais_id')
    def _check_nombre_unico(self):
        """Redefine la del mixin: el nombre solo tiene que ser único dentro de su país."""
        for record in self:
            nombre = (record.sName or '').strip().lower()
            repetidas = self.with_context(active_test=False).search([
                ('pais_id', '=', record.pais_id.id), ('id', '!=', record.id)])
            if repetidas.filtered(lambda c: (c.sName or '').strip().lower() == nombre):
                raise ValidationError("Ya existe una ciudad «%s» en %s." % (record.sName, record.pais_id.sName))

    @api.constrains('iPoblacion')
    def _check_poblacion(self):
        for record in self:
            if record.iPoblacion < 0:
                raise ValidationError("La población no puede ser negativa.")

    @api.constrains('bCapital', 'pais_id')
    def _check_una_capital(self):
        for record in self.filtered('bCapital'):
            if self.search_count([('pais_id', '=', record.pais_id.id), ('bCapital', '=', True)]) > 1:
                raise ValidationError("%s ya tiene una capital." % record.pais_id.sName)

    @api.depends('sName', 'pais_id.sName')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "%s (%s)" % (record.sName or '', record.pais_id.sName or '') \
                if record.pais_id else (record.sName or '')

    @api.onchange('bCapital', 'pais_id')
    def _onchange_capital(self):
        if self.bCapital and self.pais_id:
            capital = self.search([('pais_id', '=', self.pais_id.id), ('bCapital', '=', True),
                                   ('id', '!=', self._origin.id)], limit=1)
            if capital:
                return {'warning': {
                    'title': "Capital repetida",
                    'message': "%s ya tiene como capital a %s." % (self.pais_id.sName, capital.sName),
                }}
