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
    'depends': ['base'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # Datos iniciales (uno por entidad, 10 registros cada uno).
        # El orden importa: cada CSV va después de los catálogos a los que apunta.
        'data/uprofe.pais.csv',
        'data/uprofe.idioma.csv',
        'data/uprofe.nivel_estudios.csv',
        'data/uprofe.estado_movilidad.csv',
        'data/uprofe.estado_learning_agreement.csv',
        'data/uprofe.estado_la_linea.csv',
        'data/uprofe.universidad_destino.csv',
        # Descomentar cada línea cuando su modelo esté en main
        # (si el modelo no existe, Odoo falla al instalar/actualizar el módulo)
        # 'data/uprofe.ciudad.csv',
        # 'data/uprofe.plaza_erasmus.csv',
        # 'data/uprofe.asignatura_destino.csv',
        # 'data/uprofe.movilidad.csv',
        # 'data/uprofe.learning_agreement.csv',
        # 'data/uprofe.la_linea.csv',
        'views/estado_convenio_views.xml',
        'views/pregunta_views.xml',
        'views/persona_views.xml',
        'views/libro_inv_views.xml',
        'views/empresa_views.xml',
        'views/convenio_empresa_views.xml',
        'views/oferta_practica_views.xml',
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
        'views/menu.xml',
      
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'application': True,
}

