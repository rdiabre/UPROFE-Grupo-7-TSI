from odoo import models, fields, api

class Evento(models.Model):
    _name = 'uprofe.evento'
    _description = "Eventos de la universidad"
    _rec_name = 'sTitulo'

    sCodEvento = fields.Char(string='Código evento', required = True, copy=False)
    iAforo = fields.Integer(string='Aforo máximo')
    sTitulo = fields.Char(string='Título evento',required=True)
    sDescripcion = fields.Text(string='Descripción del evento')
    dFecha = fields.Date(string='Fecha del evento')

    fHoraIni = fields.Float(string='Hora de inicio del evento')

    #DEPENDENCIAS BLOQUEADAS#

    tipo_evento_id = fields.Many2one('uprofe.tipo_evento', string='Tipo de Evento')
    # imparte_persona_ids = fields.Many2many('uprofe.persona', 'evento_imparte_rel', 'evento_id', 'persona_id', string='Impartido por')
    # organiza_persona_ids = fields.Many2many('uprofe.persona', 'evento_organiza_rel', 'evento_id', 'persona_id', string='Organizado por')

    inscripcion_ids = fields.One2many('uprofe.evento_inscripcion', 'evento_id', string='Inscripciones')

    @api.constrains('fecha_inicio', 'fecha_fin')
    def _check_fechas_evento(self):
        for record in self:
            if record.fecha_fin and record.fecha_inicio:
                if record.fecha_fin < record.fecha_inicio:
                    raise ValidationError('La fecha de fin del evento debe ser posterior a la de inicio.')

    @api.constrains('aforo_maximo')
    def _check_aforo(self):
        for record in self:
            if record.aforo_maximo <= 0:
                raise ValidationError('El aforo máximo debe ser superior a cero.')

    
