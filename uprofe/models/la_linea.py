# -*- coding: utf-8 -*-
# Autor: Isabel Cherino

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

ESTADOS_APROBADOS = ('convalidada', 'superada')


class LaLinea(models.Model):
    """Línea de un learning agreement: una asignatura de destino que se reconoce.

    Validaciones (5+):
      1. La nota está entre 0 y 10
      2. Los créditos reconocidos no son negativos
      3. Una línea convalidada necesita nota
      4. No se reconocen más créditos que los ECTS de la asignatura
      5. Una línea convalidada o superada necesita una nota de al menos 5
      6. La asignatura es de la universidad de la movilidad
      7. El acuerdo no supera 60 créditos (reutiliza la validación del learning agreement)
    Reglas de negocio ORM (5+):
      1. Calificación en texto según la nota (compute)
      2. onchange de la asignatura: propone reconocer todos sus créditos
      3. create() numera la línea dentro de su acuerdo (search + mapped)
      4. write() al convalidar sin créditos reconoce los ECTS de la asignatura
      5. unlink() impide borrar líneas de un acuerdo aprobado
      6. Nombre a mostrar «acuerdo · nº · asignatura» (_compute_display_name)
    """
    _name = 'uprofe.la_linea'
    _description = 'Línea de learning agreement'
    _order = 'learning_agreement_id, iNum_linea'

    iNum_linea = fields.Integer(string="Nº de línea", required=True, default=0,
                                help="Se numera sola al guardar si se deja en 0.")
    fNota = fields.Float(string="Nota (0-10)")
    fCreditos_reconocidos = fields.Float(string="Créditos reconocidos")
    sObservaciones = fields.Text(string="Observaciones")

    learning_agreement_id = fields.Many2one(
        'uprofe.learning_agreement',
        string="Learning agreement",
        required=True,
        ondelete='cascade',
    )
    asignatura_destino_id = fields.Many2one(
        'uprofe.asignatura_destino',
        string="Asignatura de destino",
        required=True,
        ondelete='restrict',
    )
    estado_id = fields.Many2one(
        'uprofe.estado_la_linea',
        string="Estado",
        required=True,
        ondelete='restrict',
        default=lambda self: self.env['uprofe.estado_la_linea']._estado_inicial(),
    )
    fCreditos_ects = fields.Float(related='asignatura_destino_id.fCreditos_ects', string="ECTS de la asignatura")
    universidad_id = fields.Many2one(related='asignatura_destino_id.universidad_id', string="Universidad", store=True)
    sCalificacion = fields.Char(string="Calificación", compute='_compute_calificacion', store=True)

    asignatura_id = fields.Many2one(
        'uprofe.asignatura',
        string="Asignatura propia que se reconoce",
        required=True,
        ondelete='restrict',
    )

    _sql_constraints = [
        ('linea_unica_por_la', 'UNIQUE(learning_agreement_id, "iNum_linea")',
         'Ya existe una línea con ese número en este learning agreement.'),
    ]

    # ------------------------------------------------------------------ validaciones
    @api.constrains('fNota')
    def _check_nota(self):
        for record in self:
            if record.fNota and not (0 <= record.fNota <= 10):
                raise ValidationError("La nota debe estar entre 0 y 10.")

    @api.constrains('fCreditos_reconocidos')
    def _check_creditos(self):
        for record in self:
            if record.fCreditos_reconocidos < 0:
                raise ValidationError("Los créditos reconocidos no pueden ser negativos.")

    @api.constrains('estado_id', 'fNota')
    def _check_nota_si_convalidada(self):
        for record in self:
            if record.estado_id.sName == 'convalidada' and not record.fNota:
                raise ValidationError("Una línea convalidada necesita tener nota.")

    @api.constrains('fCreditos_reconocidos', 'asignatura_destino_id')
    def _check_creditos_maximos(self):
        for record in self:
            if record.fCreditos_reconocidos > record.asignatura_destino_id.fCreditos_ects:
                raise ValidationError("No se pueden reconocer más créditos (%.1f) que los ECTS de la asignatura (%.1f)."
                                      % (record.fCreditos_reconocidos, record.asignatura_destino_id.fCreditos_ects))

    @api.constrains('estado_id', 'fNota')
    def _check_nota_aprobado(self):
        for record in self:
            if record.estado_id.sName in ESTADOS_APROBADOS and record.fNota and record.fNota < 5:
                raise ValidationError("Una línea %s necesita una nota de al menos 5." % record.estado_id.sName)

    @api.constrains('asignatura_destino_id', 'learning_agreement_id')
    def _check_universidad(self):
        for record in self:
            universidad = record.learning_agreement_id.movilidad_id.universidad_id
            if universidad and record.asignatura_destino_id.universidad_id != universidad:
                raise ValidationError("%s no es de %s, la universidad de la movilidad."
                                      % (record.asignatura_destino_id.sName, universidad.sName))

    @api.constrains('asignatura_destino_id', 'learning_agreement_id')
    def _check_creditos_acuerdo(self):
        self.mapped('learning_agreement_id')._check_creditos_maximos()

    # ------------------------------------------------------------------ reglas de negocio
    @api.depends('fNota')
    def _compute_calificacion(self):
        for record in self:
            nota = record.fNota
            if not nota:
                record.sCalificacion = False
            elif nota < 5:
                record.sCalificacion = 'Suspenso'
            elif nota < 7:
                record.sCalificacion = 'Aprobado'
            elif nota < 9:
                record.sCalificacion = 'Notable'
            else:
                record.sCalificacion = 'Sobresaliente'

    @api.onchange('asignatura_destino_id')
    def _onchange_asignatura(self):
        if self.asignatura_destino_id and not self.fCreditos_reconocidos:
            self.fCreditos_reconocidos = self.asignatura_destino_id.fCreditos_ects

    @api.model_create_multi
    def create(self, vals_list):
        siguiente = {}
        for vals in vals_list:
            la_id = vals.get('learning_agreement_id')
            if not vals.get('iNum_linea') and la_id:
                if la_id not in siguiente:
                    usados = self.search([('learning_agreement_id', '=', la_id)]).mapped('iNum_linea')
                    siguiente[la_id] = max(usados or [0]) + 1
                vals['iNum_linea'] = siguiente[la_id]
                siguiente[la_id] += 1
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        if vals.get('estado_id') and 'fCreditos_reconocidos' not in vals:
            sin_creditos = self.filtered(lambda l: l.estado_id.sName == 'convalidada' and not l.fCreditos_reconocidos)
            for linea in sin_creditos:
                linea.fCreditos_reconocidos = linea.asignatura_destino_id.fCreditos_ects
        return res

    def unlink(self):
        bloqueadas = self.filtered(lambda l: l.learning_agreement_id.estado_id.sName == 'aprobado')
        if bloqueadas:
            raise UserError("No se pueden borrar líneas de un learning agreement aprobado. "
                            "Crea una nueva versión del acuerdo.")
        return super().unlink()

    @api.depends('learning_agreement_id.sNum_la', 'iNum_linea', 'asignatura_destino_id.sName')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "%s · %s · %s" % (record.learning_agreement_id.sNum_la or '',
                                                    record.iNum_linea, record.asignatura_destino_id.sName or '')
