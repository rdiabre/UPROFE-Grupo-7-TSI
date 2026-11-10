# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta

import pytz # para convertir a UTC (odoo guarda las fechas así)

from odoo import models, fields, api

# Horario y duración de las sesiones (en horas: 8.5 = 8:30)
HORA_MIN = 8.0
HORA_MAX = 22.0
DURACION_MIN = 0.5
DURACION_MAX = 6.0
DURACION_POR_DEFECTO = 1.5
ZONA_HORARIA = 'Europe/Madrid'

def hora_a_texto(hora):
    """8.5 -> '08:30'"""
    return f"{int(hora):02d}:{round((hora % 1) * 60):02d}"

class Sesion(models.Model):
    _name = 'uprofe.sesion'
    _description = 'UPROFE Sesión'
    _order = 'dFecha asc, fHora_ini asc'

    # Una sesión es de una asignatura (1,1); si se borra la asignatura, se borran sus sesiones
    asignatura_id = fields.Many2one('uprofe.asignatura', string="Asignatura", required=True)
    # Tipo de sesión de la sesión
    tipo_sesion_id = fields.Many2one('uprofe.tipo_sesion', string="Tipo de sesión", required=True)
    # Una sesión la imparten uno o varios profesores (1,N) y un profesor imparte varias sesiones (0,N)
    profesor_ids = fields.Many2many('uprofe.profesor', 'uprofe_profesor_sesion_rel', 'sesion_id', 'profesor_id',
                                    string="Profesores")
    # AULA (1,1) y ALUMNO (se matricula, 0,N) se añadirán cuando existan esos modelos: un Many2one o Many2many a un modelo que todavía no existe impide instalar el módulo.

    # Atributos del diagrama E-R (iN_sesion es la clave, junto con la asignatura)
    iN_sesion = fields.Integer(string="Número de sesión", required=True, default=1)
    dFecha = fields.Date(string="Fecha", required=True, default=fields.Date.context_today)
    fHora_ini = fields.Float(string="Hora de inicio", required=True, default=9.0)
    fHora_fin = fields.Float(string="Hora de fin", required=True, default=9.0 + DURACION_POR_DEFECTO)

    # Campos calculados
    fDuracion = fields.Float(string="Duración (horas)", compute='_compute_duracion', store=True)
    # Fecha y hora completas de inicio y fin: las usa la vista calendario. Tienen "inverse" para que, al arrastrar una sesión en el calendario, se cambien la fecha y las horas.
    dtInicio = fields.Datetime(string="Inicio", compute='_compute_inicio_fin', inverse='_inverse_inicio_fin',
                             store=True, readonly=False)
    dtFin = fields.Datetime(string="Fin", compute='_compute_inicio_fin', inverse='_inverse_inicio_fin',
                          store=True, readonly=False)

    # El número de sesión no se puede repetir dentro de una asignatura
    _sql_constraints = [
        ('asignatura_n_sesion_unique', 'unique(asignatura_id, "iN_sesion")',
         'Ya existe una sesión con ese número en esta asignatura.'),
    ]

    # Nombre que se muestra: "702023 · Sesión 3 (Enseñanzas Básicas)"
    @api.depends('asignatura_id', 'iN_sesion', 'tipo_sesion_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = (f"{record.asignatura_id.sCod_asig or ''} · Sesión {record.iN_sesion}"
                                   f" ({record.tipo_sesion_id.name or ''})")

    @api.depends('fHora_ini', 'fHora_fin')
    def _compute_duracion(self):
        for record in self:
            record.fDuracion = record.fHora_fin - record.fHora_ini

    # Las horas se escriben en hora de Madrid, pero Odoo guarda las fechas con hora en UTC: hay que convertirlas para que el calendario las muestre bien.
    def _zona_horaria(self):
        return pytz.timezone(self.env.context.get('tz') or self.env.user.tz or ZONA_HORARIA)

    @api.depends('dFecha', 'fHora_ini', 'fHora_fin')
    def _compute_inicio_fin(self):
        zona = self._zona_horaria()
        for record in self:
            if record.dFecha:
                medianoche = datetime.combine(record.dFecha, time())
                inicio = zona.localize(medianoche + timedelta(hours=record.fHora_ini))
                fin = zona.localize(medianoche + timedelta(hours=record.fHora_fin))
                record.dtInicio = inicio.astimezone(pytz.utc).replace(tzinfo=None)
                record.dtFin = fin.astimezone(pytz.utc).replace(tzinfo=None)
            else:
                record.dtInicio = False
                record.dtFin = False

    """Al mover la sesión en el calendario: de UTC a hora de Madrid -> fecha y horas.
    Se calculan los tres valores y se guardan juntos con un solo write(): si se asignaran
    uno a uno, la validación de las horas saltaría con la hora de inicio nueva y la de fin vieja."""
    def _inverse_inicio_fin(self):
        zona = self._zona_horaria()
        for record in self:
            valores = {}
            if record.dtInicio:
                inicio = pytz.utc.localize(record.dtInicio).astimezone(zona)
                valores['dFecha'] = inicio.date()
                valores['fHora_ini'] = inicio.hour + inicio.minute / 60
            if record.dtFin:
                fin = pytz.utc.localize(record.dtFin).astimezone(zona)
                valores['fHora_fin'] = fin.hour + fin.minute / 60
            record.write(valores)
            
    # Número de sesión mayor que 0
    @api.constrains('iN_sesion')
    def _check_n_sesion(self):
        for record in self:
            if record.iN_sesion <= 0:
                raise models.ValidationError("El número de sesión debe ser mayor que 0.")

    # Horas: la de fin después de la de inicio, dentro del horario de clases y con una duración razonable
    @api.constrains('fHora_ini', 'fHora_fin')
    def _check_horas(self):
        for record in self:
            if record.fHora_fin <= record.fHora_ini:
                raise models.ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
            if record.fHora_ini < HORA_MIN or record.fHora_fin > HORA_MAX:
                raise models.ValidationError(f"Las sesiones deben estar entre las {hora_a_texto(HORA_MIN)} "
                                      f"y las {hora_a_texto(HORA_MAX)}.")
            duracion = record.fHora_fin - record.fHora_ini
            if not DURACION_MIN <= duracion <= DURACION_MAX:
                raise models.ValidationError(f"Una sesión debe durar entre {int(DURACION_MIN * 60)} minutos "
                                      f"y {int(DURACION_MAX)} horas.")

    # Las sesiones son de lunes a viernes
    @api.constrains('dFecha')
    def _check_fecha(self):
        for record in self:
            if record.dFecha and record.dFecha.weekday() >= 5:
                raise models.ValidationError("No se pueden programar sesiones en sábado ni en domingo.")

    # Al menos un profesor. Se añade 'asignatura_id' para que la validación salte
    # también al crear la sesión sin profesores.
    @api.constrains('profesor_ids', 'asignatura_id')
    def _check_profesores(self):
        for record in self:
            if not record.profesor_ids:
                raise models.ValidationError("La sesión debe tener al menos un profesor.")

    # Un profesor no puede impartir dos sesiones a la misma hora
    @api.constrains('profesor_ids', 'dFecha', 'fHora_ini', 'fHora_fin')
    def _check_solapamiento(self):
        for record in self:
            solapada = self.search([
                ('id', '!=', record.id),
                ('dFecha', '=', record.dFecha),
                ('profesor_ids', 'in', record.profesor_ids.ids),
                ('fHora_ini', '<', record.fHora_fin),
                ('fHora_fin', '>', record.fHora_ini),
            ], limit=1)
            if solapada:
                profesores = (solapada.profesor_ids & record.profesor_ids).mapped('name')
                raise models.ValidationError(f"{', '.join(profesores)} ya tiene la sesión «{solapada.display_name}» "
                                      f"de {hora_a_texto(solapada.fHora_ini)} a {hora_a_texto(solapada.fHora_fin)} ese día.")

    # Al elegir la asignatura, propone el siguiente número de sesión
    @api.onchange('asignatura_id')
    def _onchange_asignatura(self):
        if self.asignatura_id and not self._origin.id:
            ultima = self.search([('asignatura_id', '=', self.asignatura_id.id)], order='iN_sesion desc', limit=1)
            self.iN_sesion = ultima.iN_sesion + 1 if ultima else 1

    # Al cambiar la hora de inicio, si la de fin queda antes, se pone la duración por defecto
    @api.onchange('fHora_ini')
    def _onchange_hora_ini(self):
        if self.fHora_ini and self.fHora_fin <= self.fHora_ini:
            self.fHora_fin = self.fHora_ini + DURACION_POR_DEFECTO
