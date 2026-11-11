from odoo import models, fields, api
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
