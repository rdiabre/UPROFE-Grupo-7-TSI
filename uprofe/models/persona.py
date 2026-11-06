# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api
from stdnum.es import nif  # Librería que ya viene instalada con Odoo, usada por el módulo base_vat

# Límites y formatos MAX_NOMBRE = 50
MAX_NOMBRE = 50
MAX_APELLIDOS = 100
# Letras (con tildes, ñ y ü), espacios, guiones y apóstrofoe Ej: "José Ignacio, "Pérez-Castejón, "O'Neill"
REGEX_TEXTO = r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü' -]+$"
REGEX_CORREO = r'^[\w\.-]+@[\w\.-]+\.\w+$'  # El mismo que en USUARIO
# 9 cifras empezando por 6, 7, 8 o 9, con +34 delante opcional. Ej: 612345678, +34954123456
REGEX_TELEFONO = r'^(\+34)?[6789]\d{8}$'


class Persona(models.Model):
    _name = 'uprofe.persona'
    _description = 'UPROFE Persona'
    _order = 'name asc'  # Igual que en USUARIO

    """Herencia por delegación: cada persona tiene un contacto de Odoo
    (res.partner) y usa sus campos como si fueran propios:
    name (nombre), email, phone (teléfono), ..."""
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', string="Contacto", required=True, ondelete='cascade')

    # Campos propios de Persona
    s_apellidos = fields.Char(string="Apellidos", required=True)
    s_dni = fields.Char(string="DNI", size=9, required=True, help="Inserte el DNI o NIE de la persona")

    """Unicidad del DNI: crea un índice sobre la columna, así Postgre no lee
    la tabla entera para comprobarlo. (El correo y el teléfono no se pueden
    hacer así porque se guardan en la tabla de res.partner, no en la de persona)"""
    _sql_constraints = [
        ('dni_unique', 'unique(s_dni)', 'Ya existe una persona con este DNI.'),
    ]

    """VALIDACIONES (@api.constrains): impiden guardar si algo está mal
    name, email y phone vienen de res.partner: hay que añadir 'partner_id'
    para que la validación salte también al crear la persona."""

    # Formato y letra del DNI
    @api.constrains('s_dni')
    def _check_dni(self):
        for record in self:  # cada persona que se está creando o modificando (en caché => no hay acceso a BD)
            if not nif.is_valid(record.s_dni):
                raise models.ValidationError("El DNI/NIE no es válido.")

    # Nombre: no vacío, máximo de caracteres y solo letras
    @api.constrains('name', 'partner_id')
    def _check_nombre(self):
        for record in self:
            nombre = (record.name or '').strip()
            if not nombre:
                raise models.ValidationError("El nombre no puede estar vacío.")
            if len(nombre) > MAX_NOMBRE:
                raise models.ValidationError(f"El nombre no puede tener más de {MAX_NOMBRE} caracteres.")
            if not re.match(REGEX_TEXTO, nombre):
                raise models.ValidationError("El nombre solo puede contener letras, espacios y guiones.")

    # Apellidos: no vacíos, máximo de caracteres y solo letras
    @api.constrains('apellidos')
    def _check_apellidos(self):
        for record in self:
            apellidos = (record.apellidos or '').strip()
            if not apellidos:
                raise models.ValidationError("Los apellidos no pueden estar vacíos.")
            if len(apellidos) > MAX_APELLIDOS:
                raise models.ValidationError(f"Los apellidos no pueden tener más de {MAX_APELLIDOS} caracteres.")
            if not re.match(REGEX_TEXTO, apellidos):
                raise models.ValidationError("Los apellidos solo pueden contener letras, espacios y guiones.")

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
            if self.search_count([('id', '!=', record.id), ('email', '=ilike', correo)]):
                raise models.ValidationError("Ya existe una persona con este correo electrónico.")

    # Teléfono: obligatorio, solo números (9 cifras, +34 opcional) y único
    @api.constrains('phone', 'partner_id')
    def _check_telefono(self):
        for record in self:
            telefono = (record.phone or '').replace(' ', '')
            if not telefono:
                raise models.ValidationError("El teléfono no puede estar vacío.")
            if not re.match(REGEX_TELEFONO, telefono):
                raise models.ValidationError("El teléfono debe tener 9 cifras y empezar por 6, 7, 8 o 9 (también puede empezar por +34).")
            if self.search_count([('id', '!=', record.id), ('phone', '=', record.phone)]):
                raise models.ValidationError("Ya existe una persona con este teléfono.")

    """ONCHANGE: solo en el formulario, mientras se escribe. Dejan los datos
    limpios (así las validaciones y la unicidad comparan bien).
    Siempre con if: el onchange también se ejecuta con el campo vacío. Si no se pone, da false y False.strip(), por ejemplo, no existe """

    # DNI en mayúsculas, sin espacios ni guiones
    @api.onchange('s_dni')
    def _onchange_dni(self):
        if self.s_dni:
            self.s_dni = nif.compact(self.s_dni)

    # Nombre y apellidos sin espacios sobrantes y con la inicial en mayúscula
    @api.onchange('name')
    def _onchange_nombre(self):
        if self.name:
            self.name = self.name.strip().title()

    @api.onchange('apellidos')
    def _onchange_apellidos(self):
        if self.s_apellidos:
            self.s_apellidos = self.s_apellidos.strip().title()

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