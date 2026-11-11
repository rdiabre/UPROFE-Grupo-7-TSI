# -*- coding: utf-8 -*-

from odoo import models, fields, api

MAX_DESPACHO = 30

class Profesor(models.Model):
    _name = 'uprofe.profesor'
    _description = 'UPROFE Profesor'
    _order = 'sApellidos asc, name asc'

    # Herencia por delegación: cada profesor es una persona
    _inherits = {'uprofe.persona': 'persona_id'}

    persona_id = fields.Many2one('uprofe.persona', string="Persona", required=True, ondelete='cascade') # Aquí si ponemos el ondelete. Se ha visto un caso similar en el Tema 5
    departamento_id = fields.Many2one('uprofe.departamento', string="Departamento", ondelete='restrict')
    # Campos propios de Profesor
    sDespacho = fields.Char(string="Despacho", help="Despacho del profesor. Por ejemplo: 11.2.14")
    bDoctor = fields.Boolean(string="Doctor", default=False, help="Marcar si el profesor es doctor")
    bTutor_interno = fields.Boolean(string="Tutor interno", default=False, help="Marcar si el profesor puede tutorizar alumnos internos")
    
    # Las relaciones con asignaturas y tutorías se añadirán cuando existan esos modelos.
    
    # Un profesor imparte varias sesiones (0,N) y una sesión la pueden impartir varios profesores (1,N): Many2many.
    sesion_ids = fields.Many2many('uprofe.sesion', string="Sesiones")

    # Tipos de sesión que imparte de verdad, calculado a partir de sus sesiones
    tipo_sesion_ids = fields.Many2many('uprofe.tipo_sesion', string="Tipos de sesión que imparte", compute='_compute_tipo_sesion_ids')

    selDoctor = fields.Selection([('no', 'No doctor'), ('si', 'Doctor')], string="¿Doctor?", compute='_compute_pivot', store=True)
    selTutor_interno = fields.Selection([('no', 'No es tutor interno'), ('si', 'Tutor interno')], string="¿Tutor interno?", compute='_compute_pivot', store=True)
    # Horas de clase que imparte en total
    fHoras_impartidas = fields.Float(string="Horas impartidas", compute='_compute_horas_impartidas')

    # Una persona solo puede ser un profesor una vez
    _sql_constraints = [
        ('persona_unique', 'unique(persona_id)', 'Esta persona ya está registrada como profesor.'),
    ]

    @api.depends('sesion_ids.tipo_sesion_id')
    def _compute_tipo_sesion_ids(self):
        for record in self:
            record.tipo_sesion_ids = record.sesion_ids.mapped('tipo_sesion_id') # eb, epd, ...

    @api.depends('sesion_ids.fDuracion')
    def _compute_horas_impartidas(self):
        for record in self:
            record.fHoras_impartidas = sum(record.sesion_ids.mapped('fDuracion')) # 1, 1.5, ...

    @api.depends('bDoctor', 'bTutor_interno')
    def _compute_pivot(self):
        for record in self:
            record.selDoctor = 'si' if record.bDoctor else 'no'
            record.selTutor_interno = 'si' if record.bTutor_interno else 'no'

    # Ni 0 ni mayor que 30
    @api.constrains('sDespacho')
    def _check_despacho(self):
        for record in self:
            if record.sDespacho:
                despacho = record.sDespacho.strip()
                if not despacho:
                    raise models.ValidationError("El despacho no puede estar vacío.")
                if len(despacho) > MAX_DESPACHO:
                    raise models.ValidationError(f"El despacho no puede tener más de {MAX_DESPACHO} caracteres.")

    # Despacho sin espacios a los extremos
    @api.onchange('sDespacho')
    def _onchange_despacho(self):
        if self.sDespacho:
            self.sDespacho = self.sDespacho.strip()
            