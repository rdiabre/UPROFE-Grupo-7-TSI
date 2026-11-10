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
        'views/persona_views.xml',
        'views/ubicacion_views.xml',
        'views/edificio_views.xml',
        'views/espacio_views.xml',
        'views/sala_estudio_views.xml',
        'views/inventario_views.xml',
        'views/objeto_inventariable_views.xml',
        'views/incidencia_views.xml',
        'views/horario_disponibilidad_views.xml',
        'views/reserva_horario_views.xml',
        'views/menu.xml',
        'views/catalogos_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'application': True,
}

