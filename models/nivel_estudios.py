# -*- coding: utf-8 -*-
# Autor: Isabel Cherino

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class NivelEstudios(models.Model):
    """Nivel de estudios de una plaza (grado, máster, doctorado...).

    Hereda de uprofe.catalogo_mixin (nombre, secuencia, archivado y nº de usos).
    Validaciones (5+):
      1. Nombre no vacío                       (catalogo_mixin)
      2. Nombre único sin distinguir mayúsculas (catalogo_mixin + SQL)
      3. Secuencia no negativa                 (catalogo_mixin)
      4. El nombre va en minúsculas, sin tildes y con guion bajo
      5. La duración del nivel está entre 1 y 6 años
    Reglas de negocio ORM (5+):
      1. create() normaliza el nombre a formato código (catalogo_mixin + _normalizar_nombre)
      2. write() normaliza el nombre           (catalogo_mixin)
      3. unlink() impide borrar un nivel con plazas (catalogo_mixin)
      4. copy_data() genera un nombre nuevo al duplicar (catalogo_mixin)
      5. Nº de plazas y meses ofertados en este nivel (compute con mapped)
      6. onchange del nombre: máster y doctorado requieren titulación previa
    """
    _name = 'uprofe.nivel_estudios'
    _inherit = 'uprofe.catalogo_mixin'
    _description = 'Nivel de estudios'
    _campos_uso = ('plaza_ids',)

    sName = fields.Char(string="Nombre del nivel", size=30, required=True)
    iDuracion_anios = fields.Integer(string="Duración (años)", default=1)
    bRequiere_titulo_previo = fields.Boolean(string="Requiere titulación previa")

    plaza_ids = fields.One2many('uprofe.plaza_erasmus', 'nivel_estudios_id', string="Plazas")
    iMeses_ofertados = fields.Integer(string="Meses ofertados", compute='_compute_meses_ofertados',
                                      help="Suma de la duración de todas las plazas de este nivel.")

    _sql_constraints = [
        ('nombre_unico', 'UNIQUE("sName")', 'Ya existe un nivel de estudios con ese nombre.'),
    ]

    @api.constrains('sName')
    def _check_nombre_format(self):
        regex_nombre = r'^[a-z]+(_[a-z]+)*$'
        for record in self:
            if not re.match(regex_nombre, (record.sName or '').strip()):
                raise ValidationError(
                    "El nombre va en minúsculas, sin tildes ni espacios "
                    "(por ejemplo 'grado', 'master' o 'doctorado')."
                )

    @api.constrains('iDuracion_anios')
    def _check_duracion(self):
        for record in self:
            if not 1 <= record.iDuracion_anios <= 6:
                raise ValidationError("La duración de un nivel de estudios debe estar entre 1 y 6 años.")

    @api.depends('plaza_ids.iDuracion_meses')
    def _compute_meses_ofertados(self):
        for record in self:
            record.iMeses_ofertados = sum(record.plaza_ids.mapped('iDuracion_meses'))

    @api.onchange('sName')
    def _onchange_nombre(self):
        if self.sName:
            self.sName = self._normalizar_nombre(self.sName)
            self.bRequiere_titulo_previo = self.sName.startswith(('master', 'doctorado', 'posgrado'))

    @api.model
    def _normalizar_nombre(self, nombre):
        return self.env['uprofe.estado_mixin']._normalizar_nombre(nombre)

    def _nombre_copia(self, nombre):
        return '%s_copia' % nombre
