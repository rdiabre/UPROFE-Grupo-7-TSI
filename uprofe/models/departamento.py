# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api

MAX_CODIGO = 5
MAX_NOMBRE = 50
MAX_AREA = 100
#letras mayúsc, númers y guiones, sin espacios
REGEX_CODIGO = r'^[A-Z0-9-]+$'

class Departamento(models.Model):
    _name = 'uprofe.departamento'
    _description = 'Departamento'
    _order = 'name asc'

    sCod_departamento = fields.Char(string="Código", required=True, help="Código del departamento. Ejemplo: RBT")
    name = fields.Char(string="Nombre", required = True)
    sArea_conocimiento = fields.Char(string="Área de conocimiento")

    #en un departamento puede haber muchos profesores
    lProfesor_ids = fields.One2many('uprofe.profesor', 'iDepartamento_id', string="Profesores")
 
    #un departamento puede pertenecer a varios grupos
    lGrupo_inv_ids = fields.One2many('uprofe.grupo_inv', 'iDepartamento_id', string="Grupos de investigación")

    #estos campos se rellenan con la funcion del final; se usan en la lista y el formulario como resumen
    iNum_profesores = fields.Integer(string="Nº de profesores", compute='_compute_totales')
    iNum_grupos = fields.Integer(string="Nº de grupos de investigación", compute='_compute_totales')


    #las aplica directamente postgreSQL con un indice, creo que es mas rapido y seguro
    #impide que dos departamentos tengan el mismo código
    _sql_constraints = [
        ('cod_departamento_unique', 'unique("sCod_departamento")', 'Ya existe un departamento con este código')
    ]

    #calcula el nombre que se muestra en el desplegable de otros modelos
    @api.depends('sCod_departamento', 'name')
    def _compute_display_name(self):
        for record in self:
            if record.sCod_departamento:
                record.display_name = f"[{record.sCod_departamento}] {record.name or ''}"
            else: #si no hay código, se muestra el nombre
                record.display_name = record.name

    #cuenta cuántos profesores y cuántos grupos de investigación tiene el departamento
    #se recalcula sola ante una inserción o eliminación
    @api.depends('lProfesor_ids', 'lGrupo_inv_ids')
    def _compute_totales(self):
        for record in self:
            record.iNum_profesores = len(record.lProfesor_ids)
            record.iNum_grupos = len(record.lGrupo_inv_ids)

    @api.constrains('sCod_departamento')
    def _check_codigo(self):
        for record in self: #or '' evita error si el campo está vacío
            codigo = (record.sCod_departamento or '').strip()
            if not codigo:
                raise models.ValidationError("El código del departamento no puede estar vacío")
            if len(codigo) > MAX_CODIGO:
                raise models.ValidationError(f"El código no puede tener más de {MAX_CODIGO} caracteres")
            if not re.match(REGEX_CODIGO, codigo):
                raise models.ValidationError("El código solo puede contener letras mayúsculas, números y guiones, sin espacios")

    @api.constrains('name')
    def _check_nombre(self):
        for record in self:
            nombre = (record.name or '').strip()
            if not nombre:
                raise models.ValidationError("El nombre del departamento no puede estar vacío")
            if len(nombre) > MAX_NOMBRE:
                raise models.ValidationError(f"El nombre no puede tener más de {MAX_NOMBRE}")

    #busca otro departamento distinto del actual con el mismo nombre. ilike ignora las mayúsculas
            if self.search_count([('id', '!=', record.id),('name', '=ilike', nombre)]):
                raise models.ValidationError("Ya existe un departamento con este nombre")

    @api.constrains('sArea_conocimiento')
    def _check_area_conocimiento(self):
        for record in self:
            if record.sArea_conocimiento:
                area = record.sArea_conocimiento.strip()
                if not area:
                    raise models.ValidationError("El área de conocimiento no puede estar vacía")
                if len(area) > MAX_AREA:
                    raise models.ValidationError(f"El área de conocimiento no puede tener más de {MAX_AREA} caracteres")


    #codigo en mayusc y sin espacios
    @api.onchange('sCod_departamento')
    def _onchange_codigo(self):
        if self.sCod_departamento:
            self.sCod_departamento = self.sCod_departamento.replace(' ','').upper()

    #nombre sin espacios sobrantes y con la primera letra en mayusc, el resto queda igual
    @api.onchange('name')
    def _onchange_nombre(self):
        if self.name:
            nombre = self.name.strip()
            self.name = nombre[:1].upper() + nombre[1:]

    @api.onchange('sArea_conocimiento')
    def _onchange_area_conocimiento(self):
        if self.sArea_conocimiento:
            area = self.sArea_conocimiento.strip()
            self.sArea_conocimiento = area[:1].upper() + area[1:]