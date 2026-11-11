# -*- coding: utf-8 -*-
{
    'name': "uprofe",

    'summary': "Módulo de gestión de la UPO",

    'description': """
Descripción del módulo
    """,

    'author': "Grupo 7",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'maintenance', 'resource'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # Datos iniciales (uno por entidad, 10 registros cada uno).
        # El orden importa: cada CSV va después de los catálogos a los que apunta.
        # Antes de los CSV: recupera el xmlid de registros que ya existen (ver models/datos_iniciales.py)
        'data/datos_iniciales.xml',
        'data/uprofe.pais.csv',
        'data/uprofe.idioma.csv',
        'data/uprofe.nivel_estudios.csv',
        'data/uprofe.estado_movilidad.csv',
        'data/uprofe.estado_learning_agreement.csv',
        'data/uprofe.estado_la_linea.csv',
        'data/uprofe.ciudad.csv',
        'data/uprofe.universidad_destino.csv',
        'data/uprofe.plaza_erasmus.csv',
        'data/uprofe.asignatura_destino.csv',
        'data/uprofe.movilidad.csv',
        'data/uprofe.learning_agreement.csv',
        'data/uprofe.la_linea.csv',
        'views/estado_convenio_views.xml',
        'views/pregunta_views.xml',
        'views/persona_views.xml',
        'views/estado_convocatoria_views.xml',
        'views/doc_adjunta_views.xml'
        'views/ubicacion_views.xml',
        'views/edificio_views.xml',
        'views/espacio_views.xml',
        'views/inventario_views.xml',
        'views/objeto_inventariable_views.xml',
        'views/incidencia_views.xml',
        'views/horario_disponibilidad_views.xml',
        'views/reserva_horario_views.xml',
        'views/acuerdo_views.xml',
        'views/seguimiento_practica_views.xml',
        'views/tasa_views.xml',
        'views/tipo_tasa_views.xml',
        'views/metodo_pago_views.xml',
        'views/recibo_views.xml',
        'views/empresa_views.xml',
        'views/direccion_views.xml',
        'views/convenio_empresa_views.xml',
        'views/oferta_practica_views.xml',
        'views/tutor_externo_views.xml',
        'views/profesor_views.xml',
        'views/tipo_sesion_views.xml',
        'views/sesion_views.xml',
        'views/tipo_respuesta_views.xml',
        'views/proyecto_investigacion_views.xml',
        'views/linea_investigacion_views.xml',
        'views/grupo_inv_views.xml',
        'views/financiacion_views.xml',
        'views/catalogos_views.xml',
        'views/movilidad_views.xml',
        'views/learning_agreement_views.xml',
        'views/la_linea_views.xml',
        'views/plaza_erasmus_views.xml',
        'views/asignatura_destino_views.xml',
        'views/universidad_destino_views.xml',
        'views/asignatura_views.xml',
        'views/guia_docente_views.xml',
        'views/libro_views.xml',
        'views/encuesta_views.xml',
        'views/respuesta_alumno_views.xml',
        'views/seguimiento_alu_int_views.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'application': True,
}
