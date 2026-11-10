/** @odoo-module **/
/**
 * Componente OWL 4/5: BarraCreditosField (widget de campo "uprofe_barra_creditos").
 *
 * Muestra los créditos reconocidos de un learning agreement como una barra de progreso
 * respecto a otro campo del mismo registro (opción campo_total), con color según el avance.
 * Uso:  <field name="fCreditos_reconocidos" widget="uprofe_barra_creditos"
 *              options="{'campo_total': 'fCreditos_totales'}"/>
 */
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class BarraCreditosField extends Component {
    static template = "uprofe.BarraCreditosField";
    static props = {
        ...standardFieldProps,
        campoTotal: { type: String, optional: true },
    };

    get reconocidos() {
        return this.props.record.data[this.props.name] || 0;
    }

    get total() {
        return this.props.campoTotal ? this.props.record.data[this.props.campoTotal] || 0 : 0;
    }

    get porcentaje() {
        return this.total ? Math.min(100, Math.round((this.reconocidos * 100) / this.total)) : 0;
    }

    get nivel() {
        if (this.porcentaje >= 100) {
            return "completo";
        }
        return this.porcentaje >= 50 ? "medio" : "bajo";
    }

    formatear(valor) {
        return valor.toLocaleString("es-ES", { maximumFractionDigits: 1 });
    }
}

export const barraCreditosField = {
    component: BarraCreditosField,
    displayName: "Barra de créditos (UPROFE)",
    supportedTypes: ["float", "integer"],
    extractProps: ({ options }) => ({ campoTotal: options.campo_total }),
};

registry.category("fields").add("uprofe_barra_creditos", barraCreditosField);
