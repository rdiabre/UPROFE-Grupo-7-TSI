/** @odoo-module **/
/**
 * Componente OWL 2/5: TarjetaKpi.
 * Tarjeta con un indicador (valor + título + icono). Es un componente "tonto":
 * recibe todo por props y avisa al padre con el callback onClick cuando se pulsa,
 * para que el padre abra la lista filtrada.
 */
import { Component } from "@odoo/owl";

export class TarjetaKpi extends Component {
    static template = "uprofe.TarjetaKpi";
    static props = {
        titulo: String,
        valor: [Number, String],
        icono: { type: String, optional: true },
        color: { type: String, optional: true },
        onClick: { type: Function, optional: true },
    };
    static defaultProps = { icono: "fa-bar-chart", color: "primary" };

    get valorFormateado() {
        const valor = this.props.valor;
        return typeof valor === "number" ? valor.toLocaleString("es-ES", { maximumFractionDigits: 1 }) : valor;
    }

    onClick() {
        if (this.props.onClick) {
            this.props.onClick();
        }
    }
}
