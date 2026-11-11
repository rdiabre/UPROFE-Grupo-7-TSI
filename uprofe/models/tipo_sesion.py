# -*- coding: utf-8 -*-

from odoo import models, fields, api

MAX_NOMBRE = 50

class TipoSesion(models.Model):
    _name = 'uprofe.tipo_sesion'
    _description = 'UPROFE Tipo de sesión'
    _order = 'name asc'

    # Desplegable para elegir el tipo. Si se elige "Otro", el tipo se escribe a mano en "name".
    selTipo = fields.Selection([('eb', 'Enseñanzas Básicas'),
                                ('epd', 'Enseñanzas Prácticas y de Desarrollo'),
                                ('otro', 'Otro'),
                                ], string="Tipo", required=True, default='eb')

    name = fields.Char(string="Tipo de sesión", required=True, default='Enseñanzas Básicas')

    # Lista de todas las sesiones de un tipo de sesión
    sesion_ids = fields.One2many('uprofe.sesion', 'tipo_sesion_id', string="Sesiones")
    
    # Unicidad de la clave primaria con índice en la base de datos
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Ya existe este tipo de sesión.'),
    ]

    @api.onchange('selTipo')
    def onchange_tipo(self):
        if self.selTipo == 'eb': 
            self.name = 'Enseñanzas Básicas'
        elif self.selTipo == 'epd':
            self.name = 'Enseñanzas Prácticas y de Desarrollo'
        else:
            self.name = ''
    
    # Por si no entran por formulario los datos, para que no haya incoherencia entre los tipos predfinidos y el nombre puesto
    @api.constrains('selTipo', 'name')
    def _check_tipo(self):
        for record in self: # Si no ponemos esto y los datos se reciben por un CSV = petardazo, porque self no es un registro sino varios
            if record.selTipo == 'eb' and record.name != 'Enseñanzas Básicas': 
                raise models.ValidationError('Si el tipo es "Enseñanzas Básicas", el nombre debe ser "Enseñanzas Básicas".')
            if record.selTipo == 'epd' and record.name != 'Enseñanzas Prácticas y de Desarrollo':
                raise models.ValidationError('Si el tipo es "Enseñanzas Prácticas y de Desarrollo", el nombre debe ser "Enseñanzas Prácticas y de Desarrollo".')
            
    # Tipo de sesión: no vacío, con máximo de caracteres y único sin distinguir mayúsculas
    @api.constrains('name')
    def _check_nombre(self):
        for record in self:
            nombre = record.name
            if not nombre or nombre.strip() == '':
                raise models.ValidationError("El tipo de sesión no puede estar vacío.")
            nombre = nombre.strip()
            if len(nombre) > MAX_NOMBRE:
                raise models.ValidationError(f"El tipo de sesión no puede tener más de {MAX_NOMBRE} caracteres.")
            if self.search([('id', '!=', record.id), ('name', '=ilike', nombre)], limit=1): # Variante de lo que hemos visto en clase (ilike). Con ilike, "Prácticas" está contenido en "Enseñanzas Prácticas ...", por tanto no se guardaría
                raise models.ValidationError("Ya existe este tipo de sesión.")

    """Sin espacios sobrantes y con la primera letra en mayúscula, respetando
    el resto tal como se escribe ("enseñanzas Básicas" -> "Enseñanzas Básicas")
    Siempre con "if": el onchange también se ejecuta con el campo vacío."""
    @api.onchange('name')
    def _onchange_nombre(self):
        if self.name:
            nombre = self.name.strip()
            self.name = nombre[:1].upper() + nombre[1:] # Solo cambia la primera letra
            
    # Campo computado (store=True para poder usarlo en la vista Graph)
    iNum_sesiones = fields.Integer( compute='_compute_estadisticas', string="Nº de sesiones", store=True)
    fHoras = fields.Float(compute='_compute_estadisticas', string="Horas programadas", store=True)
    
    @api.depends('sesion_ids', 'sesion_ids.fDuracion') # Si cambia el numero de sesiones o la duración de una de ellas, recalcula
    def _compute_estadisticas(self):
        for record in self:
            record.iNum_sesiones = len(record.sesion_ids) # Cuántas sesiones hay
            record.fHoras = sum(record.sesion_ids.mapped('fDuracion'))
