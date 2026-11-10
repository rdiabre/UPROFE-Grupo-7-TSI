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

    # Modelo intermedio para la relación "se inscribe en" con atributos propios
class EventoInscripcion(models.Model):
    _name = 'uprofe.evento_inscripcion'
    _description = 'Inscripción a Evento'

    evento_id = fields.Many2one('uprofe.evento', string='Evento', required=True, ondelete='cascade')
    # persona_id = fields.Many2one('uprofe.persona', string='Persona', required=True, ondelete='cascade')
    
    asiste = fields.Boolean(string='Asiste', default=False)
    estado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado')
    ], string='Estado', default='pendiente')
    fecha_inscripcion = fields.Date(string='Fecha de Inscripción', default=fields.Date.context_today)
