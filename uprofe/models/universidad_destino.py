# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class UniversidadDestino(models.Model):
    """Universidad de destino de las movilidades.

    Validaciones (5+):
      1. El código Erasmus solo admite mayúsculas, números, espacios y guiones (+ SQL único)
      2. El nombre tiene al menos 3 caracteres
      3. El correo de contacto tiene formato válido
      4. La web empieza por http:// o https://
      5. Imparte docencia al menos en un idioma (Many2many)
      6. Sus plazas y asignaturas usan idiomas que la universidad imparte
    Reglas de negocio ORM (5+):
      1. Nº de plazas y de asignaturas (compute)
      2. Créditos ECTS ofertados = suma de sus asignaturas (compute con mapped)
      3. create() normaliza el código Erasmus y la web
      4. write() normaliza el código Erasmus y la web
      5. onchange de la web: añade https:// si falta
      6. unlink() impide borrar una universidad con plazas o asignaturas
      7. Botón «Ver plazas»: abre sus plazas (acción con dominio)
    """
    _name = 'uprofe.universidad_destino'
    _description = 'Universidad de destino'
    _rec_name = 'sName'
    _order = 'sName'

    cod_erasmus = fields.Char(string="Código Erasmus", size=20, required=True)
    sName = fields.Char(string="Nombre", size=100, required=True)
    sWeb = fields.Char(string="Página web")
    sEmail_contacto = fields.Char(string="Correo de relaciones internacionales")
    bLogo = fields.Binary(string="Logo")

    ciudad_id = fields.Many2one(
       'uprofe.ciudad',
       string="Ciudad",
       required=True,
       ondelete='restrict',
    )

    pais_id = fields.Many2one(
       related='ciudad_id.pais_id',
       string="País",
       store=True,
    )

    # Many2many: idiomas en los que la universidad imparte docencia
    idioma_ids = fields.Many2many('uprofe.idioma', 'uprofe_universidad_idioma_rel',
                                  'universidad_id', 'idioma_id', string="Idiomas de docencia")

    # Descomentar cuando convenio tenga el campo universidad_id (inverso de esta relación)
    # convenio_ids = fields.One2many('uprofe.convenio', 'universidad_id', string="Convenios")
    plaza_ids = fields.One2many('uprofe.plaza_erasmus', 'universidad_id', string="Plazas")
    asignatura_ids = fields.One2many('uprofe.asignatura_destino', 'universidad_id', string="Asignaturas")

    iNum_plazas = fields.Integer(string="Nº de plazas", compute='_compute_totales', store=True)
    iNum_asignaturas = fields.Integer(string="Nº de asignaturas", compute='_compute_totales', store=True)
    fCreditos_ofertados = fields.Float(string="Créditos ofertados", compute='_compute_creditos', store=True)

    _sql_constraints = [
        ('cod_erasmus_unico', 'UNIQUE(cod_erasmus)',
         'Ya existe una universidad con ese código Erasmus.'),
    ]

    # ------------------------------------------------------------------ validaciones
    @api.constrains('cod_erasmus')
    def _check_cod_erasmus(self):
        regex_codigo = r'^[A-Z0-9][A-Z0-9 \-]*$'
        for record in self:
            if not re.match(regex_codigo, (record.cod_erasmus or '').strip()):
                raise ValidationError(
                    "El código Erasmus solo admite mayúsculas, números, espacios y guiones."
                )

    @api.constrains('sName')
    def _check_nombre(self):
        for record in self:
            if len((record.sName or '').strip()) < 3:
                raise ValidationError("El nombre de la universidad debe tener al menos 3 caracteres.")

    @api.constrains('sEmail_contacto')
    def _check_email(self):
        for record in self:
            if record.sEmail_contacto and not re.match(r'^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$', record.sEmail_contacto):
                raise ValidationError("El correo de contacto no tiene un formato válido.")

    @api.constrains('sWeb')
    def _check_web(self):
        for record in self:
            if record.sWeb and not re.match(r'^https?://\S+\.\S+$', record.sWeb):
                raise ValidationError("La web debe empezar por http:// o https://.")

    @api.constrains('idioma_ids')
    def _check_idiomas(self):
        for record in self:
            if not record.idioma_ids:
                raise ValidationError("La universidad debe impartir docencia al menos en un idioma.")

    @api.constrains('idioma_ids')
    def _check_idiomas_en_uso(self):
        for record in self:
            usados = record.plaza_ids.mapped('idioma_id') | record.asignatura_ids.mapped('idioma_id')
            faltan = usados - record.idioma_ids
            if faltan:
                raise ValidationError(
                    "No se puede quitar %s: hay plazas o asignaturas en ese idioma."
                    % ', '.join(faltan.mapped('sName')))

    # ------------------------------------------------------------------ reglas de negocio
    @api.depends('plaza_ids', 'asignatura_ids')
    def _compute_totales(self):
        for record in self:
            record.iNum_plazas = len(record.plaza_ids)
            record.iNum_asignaturas = len(record.asignatura_ids)

    @api.depends('asignatura_ids.fCreditos_ects')
    def _compute_creditos(self):
        for record in self:
            record.fCreditos_ofertados = sum(record.asignatura_ids.mapped('fCreditos_ects'))

    @api.model
    def _normalizar(self, vals):
        if vals.get('cod_erasmus'):
            vals['cod_erasmus'] = ' '.join(vals['cod_erasmus'].upper().split())
        if vals.get('sWeb'):
            vals['sWeb'] = self._completar_web(vals['sWeb'])
        return vals

    @api.model
    def _completar_web(self, web):
        web = (web or '').strip()
        if web and not re.match(r'^https?://', web):
            web = 'https://' + web
        return web

    @api.model_create_multi
    def create(self, vals_list):
        return super().create([self._normalizar(vals) for vals in vals_list])

    def write(self, vals):
        return super().write(self._normalizar(vals))

    @api.onchange('sWeb')
    def _onchange_web(self):
        if self.sWeb:
            self.sWeb = self._completar_web(self.sWeb)

    def unlink(self):
        con_datos = self.filtered(lambda u: u.plaza_ids or u.asignatura_ids)
        if con_datos:
            raise UserError("No se puede borrar %s porque tiene plazas o asignaturas."
                            % ', '.join(con_datos.mapped('sName')))
        return super().unlink()

    def action_ver_plazas(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Plazas de %s" % self.sName,
            'res_model': 'uprofe.plaza_erasmus',
            'view_mode': 'list,form',
            'domain': [('universidad_id', '=', self.id)],
            'context': {'default_universidad_id': self.id},
        }
