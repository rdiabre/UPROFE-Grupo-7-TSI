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
        'views/estado_convenio_views.xml',
        'views/pregunta_views.xml',
        'views/persona_views.xml',
        'views/tasa_views.xml',
        'views/tipo_tasa_views.xml',
        'views/profesor_views.xml',
        'views/tipo_sesion_views.xml',
        'views/sesion_views.xml',
        'views/tipo_respuesta_views.xml',
        'views/proyecto_investigacion_views.xml',
        'views/linea_investigacion_views.xml',
        'views/grupo_inv_views.xml',
        'views/financiacion_views.xml',
        'views/catalogos_views.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'application': True,
}

