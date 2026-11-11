from datetime import datetime, time, timedelta
import pytz

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ReservaHorario(models.Model):
    _name = "uprofe.reserva.horario"
    _description = "Reservas de horario UPO"
    _rec_name = "sNum_reserva"

    sNum_reserva = fields.Char(string="Número de reserva", required=True)

    dFecha_uso = fields.Date(string="Fecha de uso", required=True)

    dFecha_solicitud = fields.Date(
        string="Fecha de solicitud", required=True, default=fields.Date.context_today
    )

    dFecha_inicio = fields.Datetime(
        string="Fecha y hora de inicio", compute="_compute_fechas", store=True
    )

    dFecha_fin = fields.Datetime(
        string="Fecha y hora de fin", compute="_compute_fechas", store=True
    )

    state = fields.Selection(
        [
            ("pendiente", "Pendiente"),
            ("confirmada", "Confirmada"),
            ("rechazada", "Rechazada"),
            ("cancelada", "Cancelada"),
        ],
        string="Estado",
        required=True,
        default="pendiente",
    )

    persona_id = fields.Many2one(
        "uprofe.persona", string="Solicitante", required=True, ondelete="restrict"
    )

    espacio_id = fields.Many2one(
        "uprofe.espacio", string="Espacio", required=True, ondelete="restrict"
    )

    franja_ids = fields.Many2many(
        "resource.calendar.attendance",
        "uprofe_reserva_franja_rel",
        "reserva_id",
        "franja_id",
        string="Franjas horarias",
        required=True,
    )

    _sql_constraints = [
        (
            "num_reserva_unique",
            'UNIQUE("sNum_reserva")',
            "El número de reserva ya existe.",
        )
    ]

    def btn_submit_to_pendiente(self):
        self.write({"state": "pendiente"})

    def btn_submit_to_confirmado(self):
        self.write({"state": "confirmada"})

    def btn_submit_to_rechazado(self):
        self.write({"state": "rechazada"})

    def btn_submit_to_cancelado(self):
        self.write({"state": "cancelada"})

    @api.depends(
        "dFecha_uso",
        "franja_ids",
        "franja_ids.hour_from",
        "franja_ids.hour_to",
        "franja_ids.calendar_id.tz",
    )
    def _compute_fechas(self):
        for reserva in self:
            reserva.dFecha_inicio = False
            reserva.dFecha_fin = False

            if reserva.dFecha_uso and reserva.franja_ids:
                franjas = sorted(reserva.franja_ids, key=lambda f: f.hour_from)

                hora_inicio = round(franjas[0].hour_from * 60)
                hora_fin = round(franjas[-1].hour_to * 60)

                base = datetime.combine(reserva.dFecha_uso, time.min)

                inicio = base + timedelta(minutes=hora_inicio)
                fin = base + timedelta(minutes=hora_fin)

                zona = pytz.timezone(franjas[0].calendar_id.tz or "UTC")

                reserva.dFecha_inicio = (
                    zona.localize(inicio).astimezone(pytz.UTC).replace(tzinfo=None)
                )
                reserva.dFecha_fin = (
                    zona.localize(fin).astimezone(pytz.UTC).replace(tzinfo=None)
                )

    @api.constrains("franja_ids", "espacio_id", "dFecha_uso")
    def _check_franjas_contiguas(self):
        for reserva in self:
            if not reserva.franja_ids:
                continue

            calendarios = reserva.franja_ids.mapped("calendar_id")

            if len(calendarios) != 1:
                raise ValidationError(
                    "Todas las franjas deben pertenecer al mismo horario de disponibilidad."
                )

            if calendarios[0] not in reserva.espacio_id.horario_disponibilidad_ids:
                raise ValidationError(
                    "Las franjas seleccionadas no pertenecen a un horario de disponibilidad del espacio."
                )

            franjas = sorted(reserva.franja_ids, key=lambda f: f.hour_from)

            for anterior, siguiente in zip(franjas, franjas[1:]):
                fin_anterior = round(anterior.hour_to * 60)
                inicio_siguiente = round(siguiente.hour_from * 60)

                if fin_anterior != inicio_siguiente:
                    raise ValidationError(
                        "Las franjas seleccionadas deben ser consecutivas, sin huecos ni solapamientos."
                    )

            if reserva.dFecha_uso:
                for franja in franjas:
                    if int(franja.dayofweek) != reserva.dFecha_uso.weekday():
                        raise ValidationError(
                            "Las franjas seleccionadas no corresponden al día de la reserva."
                        )

                    if franja.date_from and reserva.dFecha_uso < franja.date_from:
                        raise ValidationError(
                            "La fecha de reserva es anterior al periodo de disponibilidad de una franja."
                        )

                    if franja.date_to and reserva.dFecha_uso > franja.date_to:
                        raise ValidationError(
                            "La fecha de reserva supera el periodo de disponibilidad de una franja."
                        )
    @api.onchange("espacio_id")
    def _onchange_espacio_id(self):
        self.franja_ids = [(5, 0, 0)]
    
    @api.constrains("espacio_id", "dFecha_uso", "franja_ids", "state")
    def _check_reserva_solapada(self):
        for reserva in self:
            if reserva.state not in ("pendiente", "confirmada"):
                continue

            if not reserva.dFecha_inicio or not reserva.dFecha_fin:
                continue

            otras_reservas = self.search([
                ("id", "!=", reserva.id),
                ("espacio_id", "=", reserva.espacio_id.id),
                ("dFecha_uso", "=", reserva.dFecha_uso),
                ("state", "in", ["pendiente", "confirmada"]),
            ])

            for otra in otras_reservas:
                if (
                    reserva.dFecha_inicio < otra.dFecha_fin
                    and reserva.dFecha_fin > otra.dFecha_inicio
                ):
                    raise ValidationError(
                        "Este espacio ya tiene una reserva para ese horario y fecha."
                    )