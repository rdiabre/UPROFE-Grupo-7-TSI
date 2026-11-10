/** @odoo-module **/
/**
 * Componente OWL 3/5: GraficoBarras.
 * Gráfico de barras horizontales hecho con HTML y CSS (sin librerías).
 * Recibe los datos por props ({etiqueta, valor, color}) y calcula con getters el
 * máximo, el total y el ancho de cada barra. Al pulsar una barra avisa al padre.
 */
import { Component } from "@odoo/owl";

export class GraficoBarras extends Component {
    static template = "uprofe.GraficoBarras";
    static props = {
        titulo: String,
        datos: Array,
        unidad: { type: String, optional: true },
        onSeleccion: { type: Function, optional: true },
    };
    static defaultProps = { unidad: "" };

    get maximo() {
        return Math.max(1, ...this.props.datos.map((d) => d.valor));
    }

    get total() {
        return this.props.datos.reduce((suma, d) => suma + d.valor, 0);
    }

    get barras() {
        return [...this.props.datos]
            .sort((a, b) => b.valor - a.valor)
            .map((d) => ({
                ...d,
                ancho: Math.round((d.valor * 100) / this.maximo),
                porcentaje: this.total ? Math.round((d.valor * 100) / this.total) : 0,
            }));
    }

    seleccionar(dato) {
        if (this.props.onSeleccion) {
            this.props.onSeleccion(dato);
        }
    }
}
