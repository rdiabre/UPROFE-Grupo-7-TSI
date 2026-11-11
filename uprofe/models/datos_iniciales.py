# -*- coding: utf-8 -*-
# Autor: Isabel Cherino

import csv
import logging

from odoo import api, models
from odoo.tools import file_open

_logger = logging.getLogger(__name__)

# Clave natural de cada CSV de data/ (la misma que su restricción UNIQUE).
# Se prueban en orden: si la primera no encuentra el registro, se prueba la siguiente.
# Las columnas "campo:id" son referencias por xmlid a otro CSV.
CLAVES_NATURALES = [
    ('uprofe.pais', [['sCodigo_iso'], ['sName']]),
    ('uprofe.idioma', [['sName']]),
    ('uprofe.nivel_estudios', [['sName']]),
    ('uprofe.estado_movilidad', [['sName']]),
    ('uprofe.estado_learning_agreement', [['sName']]),
    ('uprofe.estado_la_linea', [['sName']]),
    ('uprofe.tipo_convocatoria', [['name']]),
    ('uprofe.estado_convocatoria', [['name']]),
    ('uprofe.convocatoria', [['name']]),
    ('uprofe.tipo_solicitud', [['name']]),
    ('uprofe.estado_solicitud', [['name']]),
    ('uprofe.solicitud', [['name']]),
    ('uprofe.asignatura', [['sCod_asig']]),
    ('uprofe.ciudad', [['sName', 'pais_id:id']]),
    ('uprofe.universidad_destino', [['cod_erasmus']]),
    ('uprofe.plaza_erasmus', [['cod_plaza']]),
    ('uprofe.asignatura_destino', [['cod_asig_destino']]),
    ('uprofe.movilidad', [['sNum_movilidad']]),
    ('uprofe.learning_agreement', [['sNum_la']]),
    ('uprofe.la_linea', [['learning_agreement_id:id', 'iNum_linea']]),
]


class DatosIniciales(models.AbstractModel):
    """Carga segura de los CSV de data/ al instalar o actualizar el módulo.

    Odoo reconoce cada fila de un CSV por su xmlid (columna id). Si un registro existe en
    la tabla pero ha perdido su xmlid (creado a mano, importado o restos de una instalación
    anterior), Odoo intenta insertarlo otra vez y la restricción UNIQUE hace fallar la
    instalación. Este método se ejecuta antes de los CSV (data/datos_iniciales.xml) y le
    devuelve su xmlid a esos registros buscándolos por su clave natural. En una instalación
    limpia las tablas están vacías y no hace nada.
    """
    _name = 'uprofe.datos_iniciales'
    _description = 'Carga segura de los datos iniciales'

    @api.model
    def vincular_registros_existentes(self):
        Data = self.env['ir.model.data'].sudo()
        vinculados = 0
        for modelo, alternativas in CLAVES_NATURALES:
            Modelo = self.env[modelo].sudo().with_context(active_test=False)
            with file_open('uprofe/data/%s.csv' % modelo) as fichero:
                filas = list(csv.DictReader(fichero))
            for fila in filas:
                if Data.search_count([('module', '=', 'uprofe'), ('name', '=', fila['id'])]):
                    continue
                registro = self._buscar_por_clave(Modelo, fila, alternativas)
                if registro and not Data.search_count([('model', '=', modelo), ('res_id', '=', registro.id),
                                                        ('module', '=', 'uprofe')]):
                    Data.create({'module': 'uprofe', 'name': fila['id'], 'model': modelo, 'res_id': registro.id})
                    vinculados += 1
        if vinculados:
            _logger.info("uprofe: %d registros existentes vinculados de nuevo a su xmlid de data/", vinculados)
        return vinculados

    @api.model
    def _buscar_por_clave(self, Modelo, fila, alternativas):
        for columnas in alternativas:
            dominio = []
            for columna in columnas:
                valor = (fila.get(columna) or '').strip()
                if not valor:
                    break
                if columna.endswith(':id'):
                    referencia = self.env['ir.model.data'].sudo().search(
                        [('module', '=', 'uprofe'), ('name', '=', valor)], limit=1)
                    if not referencia:
                        break
                    dominio.append((columna[:-3], '=', referencia.res_id))
                else:
                    campo = Modelo._fields.get(columna)
                    if not campo:
                        # La columna ya no existe en el modelo (p. ej. un compañero renombró el campo):
                        # no se puede usar esta clave, pero no debe parar la actualización del módulo.
                        _logger.warning("uprofe: %s no tiene el campo '%s' del CSV; se ignora esa clave",
                                        Modelo._name, columna)
                        break
                    if campo.type == 'integer':
                        valor = int(valor)
                    dominio.append((columna, '=', valor))
            else:
                registro = Modelo.search(dominio, limit=1)
                if registro:
                    return registro
        return Modelo.browse()
