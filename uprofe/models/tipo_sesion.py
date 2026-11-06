# -*- coding: utf-8 -*-

from odoo import models, fields, api

MAX_NOMBRE = 50

# Opciones del desplegable. "otro" permite escribir el tipo a mano.
TIPOS = [
    ('eb', 'Enseñanzas Básicas'),
    ('epd', 'Enseñanzas Prácticas y de Desarrollo'),
    ('otro', 'Otro'),
]


class TipoSesion(models.Model):
    _name = 'uprofe.tipo_sesion'
    _description = 'UPROFE Tipo de sesión'
    _order = 'name asc'

    # Desplegable para elegir el tipo. Si se elige "Otro", el tipo se escribe a mano en "name".
    selTipo = fields.Selection(TIPOS, string="Tipo", required=True, default='eb')

    """Clave primaria del diagrama E-R (atributo tipo_sesion). Se llama "name"
    porque es el campo que Odoo muestra al seleccionar un tipo en otros modelos.
    Se calcula a partir del desplegable (compute), pero sigue siendo editable
    (readonly=False) para poder escribirlo a mano cuando se elige "Otro".
    precompute=True: se calcula antes de guardar; sin él, al ser obligatorio,
    la base de datos rechaza el registro porque llega vacío."""
    name = fields.Char(string="Tipo de sesión", required=True, compute='_compute_name', store=True, readonly=False, precompute=True)

    # La relación con las sesiones (sesion_ids) se añade en el PR del modelo Sesión: One2many hacia un modelo que todavía no existe impide instalar el módulo.
    # Un tipo de sesión tiene varias sesiones (1,N). Como Sesión tiene tipo_sesion_id con ondelete='restrict', un tipo con sesiones no se puede borrar.
    sesion_ids = fields.One2many('uprofe.sesion', 'tipo_sesion_id', string="Sesiones")
    
    # Unicidad de la clave primaria con índice en la base de datos
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Ya existe este tipo de sesión.'),
    ]

    # Rellena el tipo de sesión con la opción elegida en el desplegable. Con "Otro" se vacía para que se escriba a mano.
    @api.depends('selTipo')
    def _compute_name(self):
        opciones = dict(TIPOS)
        for record in self:
            if record.selTipo == 'otro':
                if record.name in opciones.values():
                    record.name = False
            else:
                record.name = opciones.get(record.selTipo)

    # Tipo de sesión: no vacío, con máximo de caracteres y único sin distinguir mayúsculas (_sql_constraints sí distingue: "Enseñanzas básicas" y "Enseñanzas Básicas" serían distintos)
    @api.constrains('name')
    def _check_nombre(self):
        for record in self:
            nombre = (record.name or '').strip()
            if not nombre:
                raise models.ValidationError("El tipo de sesión no puede estar vacío.")
            if len(nombre) > MAX_NOMBRE:
                raise models.ValidationError(f"El tipo de sesión no puede tener más de {MAX_NOMBRE} caracteres.")
            if self.search([('id', '!=', record.id), ('name', '=ilike', nombre)], limit=1):
                raise models.ValidationError("Ya existe este tipo de sesión.")

    """Sin espacios sobrantes y con la primera letra en mayúscula, respetando
    el resto tal como se escribe ("enseñanzas Básicas" -> "Enseñanzas Básicas")
    Siempre con "if": el onchange también se ejecuta con el campo vacío."""
    @api.onchange('name')
    def _onchange_nombre(self):
        if self.name:
            nombre = self.name.strip()
            self.name = nombre[:1].upper() + nombre[1:]