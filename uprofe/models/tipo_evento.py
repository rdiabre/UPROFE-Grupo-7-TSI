from odoo import models, fields, api

class TipoEvento(models.Model):
    _name = 'uprofe.tipo_evento'
    _description = 'Tipos de Eventos'
    _rec_name = 'sTipoEvento'

    sCodigoEvento = fields.Char(string='Código del Tipo', required=True, copy=False)
    sTipoEvento = fields.Char(string='Tipo de Evento', required=True)

    evento_ids = fields.One2many('uprofe.evento', 'tipo_evento_id', string='Eventos de este tipo')
