from odoo import models, fields, api

class ConvocatoriaAsignatura(models.Model):
    _name = 'uprofe.convocatoria_asignatura'
    _description = 'Convocatoria de Asignatura'

    # Atributos nativos
    fPorcentaje = fields.Float(string='Porcentaje (%)', required=True)
    sTipo = fields.Selection([
        ('ordinaria', 'Ordinaria'),
        ('extraordinaria', 'Extraordinaria')
    ], string='Tipo de Convocatoria', required=True)
    dFecha = fields.Date(string='Fecha', required=True)
    fHora = fields.Float(string='Hora', required=True)
    fDuracion = fields.Float(string='Duración (horas)')

    # --- DEPENDENCIAS BLOQUEADAS (Regla 2.6) ---
    # aula_id = fields.Many2one('uprofe.aula', string='Aula')
    # linea_acta_id = fields.Many2one('uprofe.linea_acta', string='Línea de Acta')
    # alumno_id = fields.Many2one('uprofe.alumno', string='Alumno') # o Many2many según cardinalidad exacta
    # asignatura_id = fields.Many2one('uprofe.asignatura', string='Asignatura')

    
