from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Pregunta(models.Model):
    _name = 'uprofe.pregunta'
    _description = 'Pregunta de encuesta'
    _order = 'num_pregunta asc'

    num_pregunta = fields.Integer(string='Número de pregunta', required=True, default=1)
    name = fields.Char(string='Texto de la pregunta', required=True)

    tipo_respuesta = fields.Selection([
        ('multiple', 'Múltiple opción'),
        ('escala', 'Escala de valoración'),
        ('texto', 'Comentario de texto'),
    ], string='Tipo de respuesta', default='multiple', required=True)

    opciones = fields.Text(string='Opciones (una por línea)')

    #lo descomento cuando uprofe.encuesta esté en main 
    # encuesta_id = fields.Many2one('uprofe.encuesta', string='Encuesta',
    #                               required=True, ondelete='cascade')

    # _sql_constraints = [
    #     ('num_pregunta_encuesta_uniq', 'unique(encuesta_id, num_pregunta)',
    #      'Ya existe una pregunta con ese número en esta encuesta.'),
    # ]

    @api.constrains('num_pregunta')
    def _check_num_pregunta(self):
        for record in self:
            if record.num_pregunta < 1:
                raise ValidationError("El número de pregunta debe ser mayor que 0.")

    @api.constrains('tipo_respuesta', 'opciones')
    def _check_opciones(self):
        for record in self:
            if record.tipo_respuesta == 'multiple':
                lineas = [l for l in (record.opciones or '').splitlines() if l.strip()]
                if len(lineas) < 2:
                    raise ValidationError("Una pregunta de múltiple opción necesita al menos dos opciones.")

    @api.onchange('tipo_respuesta')
    def _onchange_tipo_respuesta(self):
        if self.tipo_respuesta != 'multiple' and self.opciones:
            self.opciones = False
            return {
                'warning': {
                    'title': 'Opciones eliminadas',
                    'message': 'Solo las preguntas de múltiple opción tienen opciones.'
                }
            }