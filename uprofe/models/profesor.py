# -*- coding: utf-8 -*-

from odoo import models, fields, api

MAX_DESPACHO = 30


class Profesor(models.Model):
    _name = 'uprofe.profesor'
    _description = 'UPROFE Profesor'
    _order = 'apellidos asc, name asc'

    # Herencia por delegación: cada profesor es una persona
    _inherits = {'uprofe.persona': 'persona_id'}

    persona_id = fields.Many2one('uprofe.persona', string="Persona",
                                 required=True, ondelete='cascade')

    # Campos propios de Profesor
    despacho = fields.Char(string="Despacho", help="Despacho del profesor. Por ejemplo: 11.2.14")
    doctor = fields.Boolean(string="Doctor", default=False, help="Marcar si el profesor es doctor")
    tutor_interno = fields.Boolean(string="Tutor interno", default=False,
                                   help="Marcar si el profesor puede tutorizar alumnos internos")

    """Las relaciones con otros modelos (asignaturas, sesiones, tutorías...) se añadirán
    en el PR de cada uno de esos modelos
    Los tipos de sesión que imparte (EB, EPD...) no se guardan aquí: se calcularán
    a partir de sus sesiones en el PR de Sesión (sesion_ids -> tipo_sesion_id)."""
    
    """ AÑADIR EN EL PR DE SESION:
    # Sesiones que imparte el profesor (la otra cara del profesor_id de Sesión)
    sesion_ids = fields.One2many('uprofe.sesion', 'profesor_id', string="Sesiones")

    # Tipos de sesión que imparte de verdad: se calculan a partir de sus sesiones
    tipo_sesion_ids = fields.Many2many('uprofe.tipo_sesion', string="Tipos de sesión que imparte",
                                       compute='_compute_tipo_sesion_ids')

    @api.depends('sesion_ids.tipo_sesion_id')
    def _compute_tipo_sesion_ids(self):
        for record in self:
            record.tipo_sesion_ids = record.sesion_ids.mapped('tipo_sesion_id')"""

    # Una persona solo puede ser un profesor una vez
    _sql_constraints = [
        ('persona_unique', 'unique(persona_id)', 'Esta persona ya está registrada como profesor.'),
    ]

    # Ni 0 ni mayor que 30
    @api.constrains('despacho')
    def _check_despacho(self):
        for record in self:
            if record.despacho:
                despacho = record.despacho.strip()
                if not despacho:
                    raise models.ValidationError("El despacho no puede estar vacío.")
                if len(despacho) > MAX_DESPACHO:
                    raise models.ValidationError(f"El despacho no puede tener más de {MAX_DESPACHO} caracteres.")

    # Despacho sin espacios a los extremos
    @api.onchange('despacho')
    def _onchange_despacho(self):
        if self.despacho:
            self.despacho = self.despacho.strip()
            
    # Si el DNI ya es de una persona registrada, se usa esa persona en lugar de crear otra (solo al crear un profesor nuevo: self._origin.id está vacío)
    @api.onchange('dni')
    def _onchange_dni_persona_existente(self):
        if self.dni and not self._origin.id:
            persona = self.env['uprofe.persona'].search([('dni', '=ilike', self.dni.strip())], limit=1)
            if persona:
                self.persona_id = persona
                # Aviso si esa persona ya es profesor
                if self.search([('persona_id', '=', persona.id)], limit=1):
                    return {
                        'warning': {
                            'title': 'Profesor ya registrado',
                            'message': 'Ya existe un profesor con este DNI.',
                        }
                    }