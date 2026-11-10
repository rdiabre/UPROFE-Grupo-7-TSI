/** @odoo-module **/
/**
 * Componente OWL 5/5: ProgresoEstanciaField (widget de campo "uprofe_progreso_estancia").
 *
 * Se pone sobre la duración en días de una movilidad y, leyendo también las fechas de
 * inicio y fin del registro, muestra en qué punto está la estancia respecto a hoy:
 * "Empieza en N días", "Día N de M" con barra de progreso o "Terminó hace N días".
 * Uso:  <field name="iDuracion_dias" widget="uprofe_progreso_estancia"/>
 */
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

const { DateTime } = luxon;

export class ProgresoEstanciaField extends Component {
    static template = "uprofe.ProgresoEstanciaField";
    static props = {
        ...standardFieldProps,
        campoInicio: { type: String, optional: true },
        campoFin: { type: String, optional: true },
    };
    static defaultProps = { campoInicio: "dFecha_inicio", campoFin: "dFecha_fin" };

    get info() {
        const inicio = this.props.record.data[this.props.campoInicio];
        const fin = this.props.record.data[this.props.campoFin];
        const total = this.props.record.data[this.props.name] || 0;
        if (!inicio || !fin || !total) {
            return { fase: "sin_fechas", texto: "Sin fechas", porcentaje: 0, icono: "fa-question-circle" };
        }
        const hoy = DateTime.local().startOf("day");
        if (hoy < inicio.startOf("day")) {
            const dias = Math.round(inicio.startOf("day").diff(hoy, "days").days);
            return { fase: "pendiente", texto: `Empieza en ${dias} días`, porcentaje: 0, icono: "fa-hourglass-start" };
        }
        if (hoy > fin.startOf("day")) {
            const dias = Math.round(hoy.diff(fin.startOf("day"), "days").days);
            return { fase: "terminada", texto: `Terminó hace ${dias} días`, porcentaje: 100, icono: "fa-flag-checkered" };
        }
        const transcurridos = Math.round(hoy.diff(inicio.startOf("day"), "days").days) + 1;
        return {
            fase: "en_curso",
            texto: `Día ${transcurridos} de ${total}`,
            porcentaje: Math.min(100, Math.round((transcurridos * 100) / total)),
            icono: "fa-plane",
        };
    }
}

export const progresoEstanciaField = {
    component: ProgresoEstanciaField,
    displayName: "Progreso de la estancia (UPROFE)",
    supportedTypes: ["integer"],
    extractProps: ({ options }) => ({
        campoInicio: options.campo_inicio,
        campoFin: options.campo_fin,
    }),
};

registry.category("fields").add("uprofe_progreso_estancia", progresoEstanciaField);
