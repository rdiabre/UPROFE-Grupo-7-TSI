/** @odoo-module **/
/**
 * Componente OWL 1/5: PanelErasmus (acción cliente "uprofe.panel_erasmus").
 *
 * Panel de control de movilidad. Muestra:
 *   - KPI (componente hijo TarjetaKpi): al pulsarlos abre la lista filtrada.
 *   - Dos gráficos (componente hijo GraficoBarras): movilidades por estado y vacantes por país.
 *   - Las movilidades en curso y próximas, con un buscador reactivo (useState + t-model).
 *
 * Integración con el backend (Parte V): pide los datos por RPC al ORM con
 * orm.call("uprofe.movilidad", "get_datos_panel") y usa los servicios action y notification.
 */
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { TarjetaKpi } from "../tarjeta_kpi/tarjeta_kpi";
import { GraficoBarras } from "../grafico_barras/grafico_barras";

export class PanelErasmus extends Component {
    static template = "uprofe.PanelErasmus";
    static components = { TarjetaKpi, GraficoBarras };
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.state = useState({ cargando: true, datos: null, busqueda: "", soloEnCurso: false });
        onWillStart(() => this.cargarDatos());
    }

    async cargarDatos() {
        this.state.cargando = true;
        try {
            this.state.datos = await this.orm.call("uprofe.movilidad", "get_datos_panel", []);
        } catch {
            this.state.datos = null;
            this.notification.add("No se han podido cargar los datos del panel.", { type: "danger" });
        } finally {
            this.state.cargando = false;
        }
    }

    async actualizar() {
        await this.cargarDatos();
        if (this.state.datos) {
            this.notification.add("Panel actualizado.", { type: "success" });
        }
    }

    // ---------- lista de movilidades con buscador
    get movilidades() {
        const texto = this.state.busqueda.trim().toLowerCase();
        const hoy = this.state.datos.hoy;
        return this.state.datos.movilidades.filter((m) => {
            if (this.state.soloEnCurso && m.dFecha_inicio > hoy) {
                return false;
            }
            const campos = [m.sNum_movilidad, m.universidad_id && m.universidad_id[1], m.pais_id && m.pais_id[1]];
            return !texto || campos.some((c) => c && c.toLowerCase().includes(texto));
        });
    }

    fase(movilidad) {
        return movilidad.dFecha_inicio > this.state.datos.hoy ? "Próxima" : "En curso";
    }

    limpiarBusqueda() {
        this.state.busqueda = "";
    }

    // ---------- navegación (servicio action)
    abrirLista(nombre, modelo, dominio) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: nombre,
            res_model: modelo,
            domain: dominio,
            views: [[false, "list"], [false, "form"]],
        });
    }

    abrirKpi(kpi) {
        this.abrirLista(kpi.titulo, kpi.modelo, kpi.dominio);
    }

    abrirEstado(estado) {
        this.abrirLista(`Movilidades: ${estado.etiqueta}`, "uprofe.movilidad", [["estado_id", "=", estado.id]]);
    }

    abrirPais(pais) {
        this.abrirLista(`Plazas en ${pais.etiqueta}`, "uprofe.plaza_erasmus", [["pais_id", "=", pais.id]]);
    }

    abrirMovilidad(movilidad) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "uprofe.movilidad",
            res_id: movilidad.id,
            views: [[false, "form"]],
        });
    }
}

registry.category("actions").add("uprofe.panel_erasmus", PanelErasmus);
