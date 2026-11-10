# -*- coding: utf-8 -*-

from odoo import models, fields, api

# Orden de las firmas del acuerdo: cada estado incluye las firmas de los anteriores
FIRMAS = [
    ('estudiante', "Estudiante", ('firmado_estudiante', 'firmado_origen', 'firmado_destino', 'aprobado')),
    ('origen', "Coordinación de la universidad de origen (UPO)", ('firmado_origen', 'firmado_destino', 'aprobado')),
    ('destino', "Coordinación de la universidad de destino", ('firmado_destino', 'aprobado')),
]


class ReportLearningAgreement(models.AbstractModel):
    """Informe personalizado del learning agreement (Tema 7.2, plantillas personalizadas).

    Prepara para la plantilla QWeb datos que no están en el modelo: resumen por estado de
    línea, porcentaje de créditos reconocidos, historial de versiones y estado de las firmas.
    """
    _name = 'report.uprofe.report_learning_agreement'
    _description = 'Informe del learning agreement'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['uprofe.learning_agreement'].browse(docids)
        resumen = {}
        for la in docs:
            por_estado = []
            for estado in la.linea_ids.mapped('estado_id').sorted('iSecuencia'):
                lineas = la.linea_ids.filtered(lambda l: l.estado_id == estado)
                por_estado.append({
                    'estado': estado,
                    'lineas': len(lineas),
                    'creditos': sum(lineas.mapped('fCreditos_ects')),
                })
            porcentaje = round(la.fCreditos_reconocidos * 100 / la.fCreditos_totales) if la.fCreditos_totales else 0
            resumen[la.id] = {
                'porcentaje': min(porcentaje, 100),
                'por_estado': por_estado,
                'versiones': la.movilidad_id.learning_agreement_ids.sorted('iVersion'),
                'firmas': [
                    {'rol': rol, 'titulo': titulo, 'firmada': la.estado_id.sName in estados and bool(la.dFecha_firma)}
                    for rol, titulo, estados in FIRMAS
                ],
            }
        return {
            'doc_ids': docids,
            'doc_model': 'uprofe.learning_agreement',
            'docs': docs,
            'resumen': resumen,
            'fecha_emision': fields.Datetime.context_timestamp(self, fields.Datetime.now()),
            'humanizar': lambda texto: (texto or '').replace('_', ' ').capitalize(),
        }
