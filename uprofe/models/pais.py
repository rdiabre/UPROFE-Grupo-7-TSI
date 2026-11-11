# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Pais(models.Model):
    """País de destino.

    Hereda de uprofe.catalogo_mixin (nombre, secuencia, archivado y nº de usos).
    Validaciones (5+):
      1. Nombre no vacío                       (catalogo_mixin)
      2. Nombre único sin distinguir mayúsculas (catalogo_mixin)
      3. Secuencia no negativa                 (catalogo_mixin)
      4. El nombre solo admite letras, espacios y guiones
      5. El código ISO tiene 2 letras mayúsculas y es único (constrains + SQL)
    Reglas de negocio ORM (5+):
      1. create() normaliza el nombre          (catalogo_mixin)
      2. write() normaliza el nombre           (catalogo_mixin)
      3. unlink() impide borrar un país con ciudades (catalogo_mixin)
      4. copy_data() genera un nombre nuevo al duplicar (catalogo_mixin)
      5. Nº de universidades del país (search_count sobre universidad_destino)
      6. onchange del código ISO: lo pasa a mayúsculas
    """
    _name = 'uprofe.pais'
    _inherit = 'uprofe.catalogo_mixin'
    _description = 'País'
    _campos_uso = ('ciudad_ids',)

    sName = fields.Char(string="Nombre del país", size=50, required=True)
    sDescription = fields.Char(string="Descripción del país", size=150)
    sCodigo_iso = fields.Char(string="Código ISO", size=2, copy=False, help="Código ISO 3166-1 alfa-2, por ejemplo IT.")
    bUnion_europea = fields.Boolean(string="Miembro de la UE", default=True)

    ciudad_ids = fields.One2many('uprofe.ciudad', 'pais_id', string="Ciudades")
    iNum_universidades = fields.Integer(string="Nº de universidades", compute='_compute_num_universidades')

    _sql_constraints = [
        ('codigo_iso_unico', 'UNIQUE("sCodigo_iso")', 'Ya existe un país con ese código ISO.'),
    ]

    @api.constrains('sName')
    def _check_nombre_format(self):
        regex_nombre = r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'\.\-]+$"
        for record in self:
            if not re.match(regex_nombre, (record.sName or '').strip()):
                raise ValidationError(
                    "El nombre del país solo puede contener letras, espacios y guiones."
                )

    @api.constrains('sCodigo_iso')
    def _check_codigo_iso(self):
        for record in self:
            if record.sCodigo_iso and not re.match(r'^[A-Z]{2}$', record.sCodigo_iso):
                raise ValidationError("El código ISO son 2 letras en mayúsculas (por ejemplo IT).")

    def _compute_num_universidades(self):
        Universidad = self.env['uprofe.universidad_destino']
        for record in self:
            record.iNum_universidades = Universidad.search_count([('pais_id', '=', record.id)])

    @api.onchange('sCodigo_iso')
    def _onchange_codigo_iso(self):
        if self.sCodigo_iso:
            self.sCodigo_iso = self.sCodigo_iso.strip().upper()
