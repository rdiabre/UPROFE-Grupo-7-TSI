from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Tutoria(models.Model):
    _name = 'uprofe.tutoria'
    _description = 'Tutoría Programada'

    # Atributos nativos
    dFecha = fields.Date(string='Fecha', default=fields.Date.context_today, required=True)
    sUsuProfesor = fields.Char(string='Usuario Profesor', required=True)
    sUsuAlumno = fields.Char(string='Usuario Alumno', required=True)
    bTelematico = fields.Boolean(string='Es Telemática', default=False)
    bAsiste = fields.Boolean(string='Asiste', default=False)

    # Relación interna
    horario_tutoria_id = fields.Many2one('uprofe.horario_tutoria', string='Horario de Tutoría', required=True)

    fHoraIni = fields.Float(related='horario_tutoria_id.fHoraIni', string='Hora de Inicio', readonly=True)
    fHoraFin = fields.Float(related='horario_tutoria_id.fHoraFin', string='Hora de Fin', readonly=True)

    # --- DEPENDENCIAS BLOQUEADAS ---
    # alumno_id = fields.Many2one('uprofe.alumno', string='Alumno')

    @api.constrains('horario_tutoria_id')
    def _check_horario_unico(self):
        for record in self:
            duplicados = self.env['uprofe.tutoria'].search([
                ('horario_tutoria_id', '=', record.horario_tutoria_id.id),
                ('id', '!=', record.id)
            ])
            if duplicados:
                raise ValidationError("¡Este horario de tutoría ya está reservado por otro alumno! Por favor, selecciona uno distinto.")
