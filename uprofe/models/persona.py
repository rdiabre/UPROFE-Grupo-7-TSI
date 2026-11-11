# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api
from stdnum.es import nif  # Librería que ya viene instalada con Odoo, usada por el módulo base_vat

# Límites y formatos
MAX_NOMBRE = 50
MAX_APELLIDOS = 100
# Letras (con tildes, ñ y ü), espacios, guiones y apóstrofe Ej: "José Ignacio", "Pérez-Castejón", "O'Neill"
REGEX_TEXTO = r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü' -]+$"
REGEX_CORREO = r'^[\w\.-]+@[\w\.-]+\.\w+$'  
# 9 cifras empezando por 6, 7, 8 o 9, con +34 delante opcional. Ej: 612345678, +34954123456
REGEX_TELEFONO = r'^(\+34)?[6789]\d{8}$'

class Persona(models.Model):
    _name = 'uprofe.persona'
    _description = 'UPROFE Persona'
    _order = 'name asc'  # Igual que en USUARIO

    """Herencia por delegación: cada persona tiene un contacto de Odoo (res.partner) y usa sus campos como si fueran propios:
    name (nombre), email, phone (teléfono), ..."""
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', string="Contacto", required=True, ondelete='cascade')

    # Campos propios de Persona
    sApellidos = fields.Char(string="Apellidos", required=True)
    sDni = fields.Char(string="DNI", size=9, required=True, help="Inserte el DNI o NIE de la persona")
    
    inventario_ids = fields.One2many('uprofe.inventario', 'responsable_id', string="Inventarios asociados")

    direccion_id = fields.Many2one('uprofe.direccion', string="Dirección", required=True)
    
    """Unicidad del DNI: crea un índice sobre la columna, así Postgre no lee la tabla entera para comprobarlo. (El correo y el
    teléfono no se pueden hacer así porque se guardan en la tabla de res.partner, no en la de persona)"""
    _sql_constraints = [
        ('dni_unique', 'unique("sDni")', 'Ya existe una persona con este DNI.'),
    ]

    """VALIDACIONES (@api.constrains): impiden guardar si algo está mal name, email y phone vienen de res.partner: hay que añadir
    'partner_id' para que la validación salte también al crear la persona."""

    # Formato y letra del DNI
    @api.constrains('sDni')
    def _check_dni(self):
        for record in self:  # cada persona que se está creando o modificando (en caché => no hay acceso a BD)
            if not nif.is_valid(record.sDni):
                raise models.ValidationError("El DNI/NIE no es válido.")

    # Nombre: no vacío, máximo de caracteres y solo letras
    @api.constrains('name', 'partner_id')
    def _check_nombre(self):
        for record in self:
            nombre = record.name
            if not nombre or nombre.strip() == '':
                raise models.ValidationError("El nombre no puede estar vacío.")
            nombre = nombre.strip()
            if len(nombre) > MAX_NOMBRE:
                raise models.ValidationError(f"El nombre no puede tener más de {MAX_NOMBRE} caracteres.")
            if not re.match(REGEX_TEXTO, nombre):
                raise models.ValidationError("El nombre solo puede contener letras, espacios, guiones y apóstrofe.")

    # Apellidos: no vacíos, máximo de caracteres y solo letras
    @api.constrains('sApellidos')
    def _check_apellidos(self):
        for record in self:
            apellidos = record.sApellidos
            if not apellidos or apellidos.strip() == '':
                raise models.ValidationError("Los apellidos no pueden estar vacíos.")
            apellidos = apellidos.strip()
            if len(apellidos) > MAX_APELLIDOS:
                raise models.ValidationError(f"Los apellidos no pueden tener más de {MAX_APELLIDOS} caracteres.")
            if not re.match(REGEX_TEXTO, apellidos):
                raise models.ValidationError("Los apellidos solo pueden contener letras, espacios, guiones o apóstrofe.")

    # Correo: obligatorio, con formato de correo y único
    @api.constrains('email', 'partner_id')
    def _check_correo(self):
        for record in self:
            correo = (record.email or '').strip()
            if not correo:
                raise models.ValidationError("El correo electrónico no puede estar vacío.")
            if not re.match(REGEX_CORREO, correo):
                raise models.ValidationError("El correo electrónico no es válido.")
            # =ilike: no distingue mayúsculas (pepe@upo.es = PEPE@upo.es)
            if self.search([('id', '!=', record.id), ('email', '=ilike', correo)], limit=1):
                raise models.ValidationError("Ya existe una persona con este correo electrónico.")

    # Teléfono: obligatorio, solo números (9 cifras, +34 opcional) y único
    @api.constrains('phone', 'partner_id')
    def _check_telefono(self):
        for record in self:
            telefono = record.phone
            if not telefono or telefono.replace(' ', '') == '':
                raise models.ValidationError("El teléfono no puede estar vacío.")
            telefono = telefono.replace(' ', '')
            if not re.match(REGEX_TELEFONO, telefono):
                raise models.ValidationError("El teléfono debe tener 9 cifras y empezar por 6, 7, 8 o 9 (también puede empezar por +34).")
            if self.search([('id', '!=', record.id), ('phone', '=', telefono)], limit=1):
                raise models.ValidationError("Ya existe una persona con este teléfono.")

    """ONCHANGE: solo en el formulario, mientras se escribe. Dejan los datos
    limpios (así las validaciones y la unicidad comparan bien).
    Siempre con if: el onchange también se ejecuta con el campo vacío. Si no se pone, da false y False.strip(), por ejemplo, no existe """

    # DNI en mayúsculas, sin espacios ni guiones
    @api.onchange('sDni')
    def _onchange_dni(self):
        if self.sDni:
            self.sDni = nif.compact(self.sDni)

    # Nombre y apellidos sin espacios sobrantes y con la inicial en mayúscula
    @api.onchange('name')
    def _onchange_nombre(self):
        if self.name:
            self.name = self.name.strip().title()

    @api.onchange('sApellidos')
    def _onchange_apellidos(self):
        if self.sApellidos:
            self.sApellidos = self.sApellidos.strip().title()

    # Correo en minúsculas y sin espacios
    @api.onchange('email')
    def _onchange_correo(self):
        if self.email:
            self.email = self.email.strip().lower()

    # Teléfono sin espacios
    @api.onchange('phone')
    def _onchange_telefono(self):
        if self.phone:
            self.phone = self.phone.replace(' ', '')