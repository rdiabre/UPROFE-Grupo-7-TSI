/** @odoo-module **/
/**
 * Componente OWL extra: InsigniaCalificacionField (widget de campo "uprofe_insignia_calificacion").
 * Muestra la calificación de una línea (Suspenso, Aprobado, Notable, Sobresaliente)
 * como una insignia de color con un icono.
 * Uso:  <field name="sCalificacion" widget="uprofe_insignia_calificacion"/>
 */
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

const ESTILOS = {
    Suspenso: { clase: "suspenso", icono: "fa-times" },
    Aprobado: { clase: "aprobado", icono: "fa-check" },
    Notable: { clase: "notable", icono: "fa-star-half-o" },
    Sobresaliente: { clase: "sobresaliente", icono: "fa-star" },
};

export class InsigniaCalificacionField extends Component {
    static template = "uprofe.InsigniaCalificacionField";
    static props = { ...standardFieldProps };

    get calificacion() {
        return this.props.record.data[this.props.name] || "";
    }

    get estilo() {
        return ESTILOS[this.calificacion] || { clase: "vacia", icono: "fa-minus" };
    }
}

export const insigniaCalificacionField = {
    component: InsigniaCalificacionField,
    displayName: "Insignia de calificación (UPROFE)",
    supportedTypes: ["char"],
};

registry.category("fields").add("uprofe_insignia_calificacion", insigniaCalificacionField);
