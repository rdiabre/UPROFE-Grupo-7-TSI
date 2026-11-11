from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Horario_Tutoria(models.Model):
    _name = 'uprofe.horario_tutoria'
    _description = 'Horario de tutorías'

    sUsuProfesor = fields.Char(string='Usuario Profesor', required=True)
    dFecha = fields.Date(string='Fecha de Tutoría', default=fields.Date.context_today, required=True)
    fHoraIni = fields.Float(string='Hora de inicio de la tutoría.', required=True)
    fHoraFin = fields.Float(string='Hora de final de la tutoría.', required=True)

    # DEPENDENCIAS BLOQUEADAS
    # tutoria_id = fields.Many2one('uprofe.tutoria', string='Tutoría')
    # profesor_id = fields.Many2one('uprofe.profesor', string='Profesor')
    # aula_id = fields.Many2one('uprofe.aula', string='Aula')

    @api.constrains('fHoraIni', 'fHoraFin')
    def _check_horas(self):
        for record in self:
            if record.fHoraFin <= record.fHoraIni:
                raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")

    @api.constrains('hora_inicio', 'hora_fin')
    def _check_horas(self):
        for record in self:
            if record.hora_inicio >= record.hora_fin:
                raise ValidationError('La hora de inicio debe ser anterior a la hora de fin.')
            if record.hora_inicio < 0 or record.hora_fin > 24:
                raise ValidationError('Las horas deben estar comprendidas entre las 0 y las 24.')
