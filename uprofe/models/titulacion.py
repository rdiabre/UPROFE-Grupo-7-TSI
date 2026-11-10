# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api 

MAX_CODIGO = 10
MAX_NOMBRE = 100
MAX_CREDITOS = 360   #un máster/grado no pasa de aquí (grado 240, máster 60-120, doble grado ~360)
MAX_CURSOS = 6       #mismo máximo que iCurso en Asignatura
#Letras mayúsculas, números y guiones, sin espacios. Ej: GII, MU-INF
REGEX_CODIGO = r'^[A-Z0-9-]+$'


class Titulacion(models.Model):
    _name = 'uprofe.titulacion'
    _description = 'UPROFE Titulación'
    _order = 'name asc'
    _rec_names_search = ['name', 'sCod_titulacion']  #se busca por nombre o por código en los desplegables

    sCod_titulacion = fields.Char(string="Código", required=True, help="Código de la titulación. Por ejemplo: GII")
    name = fields.Char(string="Nombre", required=True)
    iCreditos_totales = fields.Integer(string="Créditos totales", required=True, default=240)
    iDuracion_cursos = fields.Integer(string="Duración (cursos)", required=True, default=4)

    #una titulación tiene AL MENOS un plan de estudio y cada plan pertenece a una sola titulación.
    #lPlan_estudio_ids = fields.One2many('uprofe.plan_estudio', 'iTitulacion_id', string="Planes de estudio")

    #una titulación puede tener cero o muchos expedientes 
    #lExpediente_ids = fields.One2many('uprofe.expediente', 'iTitulacion_id', string="Expedientes")

    lConvenio_ids = fields.Many2many('uprofe.convenio', 'uprofe_titulacion_convenio_rel',
                                     'titulacion_id', 'convenio_id', string="Convenios")

    iNum_convenios = fields.Integer(string="Nº de convenios", compute='_compute_totales')
    #creditos a superar por curso
    fCreditos_por_curso = fields.Float(string="Créditos por curso", compute='_compute_creditos_por_curso')

    _sql_constraints = [
        ('cod_titulacion_unique', 'unique("sCod_titulacion")', 'Ya existe una titulación con este código.'),
    ]

    # Se recalcula cuando se añade o quita un convenio. 
    #Cuando existan los otros modelos, añadir aqui 'lPlan_estudio_ids' y 'lExpediente_ids' (y sus contadores).
    @api.depends('lConvenio_ids')
    def _compute_totales(self):
        for record in self:
            record.iNum_convenios = len(record.lConvenio_ids)

    #depende de los dos campos que lee la funcion
    @api.depends('iCreditos_totales', 'iDuracion_cursos')
    def _compute_creditos_por_curso(self):
        for record in self:
            #si no hay duración, no se divide, pa no dividir por cero
            if record.iDuracion_cursos == 0.0:
                record.fCreditos_por_curso = 0.0
            else:
                record.fCreditos_por_curso = record.iCreditos_totales / record.iDuracion_cursos

    #Nombre en los desplegables
    @api.depends('sCod_titulacion', 'name')
    def _compute_display_name(self):
        for record in self:
            if record.sCod_titulacion:
                record.display_name = f"[{record.sCod_departamento}] {record.name or ''}"
            else:
                record.diplay_name = record.name

    @api.constrains('sCod_titulacion')
    def _check_codigo(self):
        for record in self:
            codigo = (record.sCod_titulacion or '').strip()
            if not codigo:
                raise models.ValidationError("El código de la titulación no puede estar vacío.")
            if len(codigo) > MAX_CODIGO:
                raise models.ValidationError(f"El código no puede tener más de {MAX_CODIGO} caracteres.")
            if not re.match(REGEX_CODIGO, codigo):
                raise models.ValidationError("El código solo puede contener letras mayúsculas, números y guiones, sin espacios.")

    @api.constrains('name')
    def _check_nombre(self):
        for record in self:
            nombre = (record.name or '').strip()
            if not nombre:
                raise models.ValidationError("El nombre de la titulación no puede estar vacío.")
            if len(nombre) > MAX_NOMBRE:
                raise models.ValidationError(f"El nombre no puede tener más de {MAX_NOMBRE} caracteres.")
            if self.search_count([('id', '!=', record.id), ('name', '=ilike', nombre)]):
                raise models.ValidationError("Ya existe una titulación con este nombre.")

    # Mayores que 0 y con un máximo razonable
    @api.constrains('iCreditos_totales')
    def _check_creditos(self):
        for record in self:
            if record.iCreditos_totales <= 0:
                raise models.ValidationError("Los créditos totales deben ser mayores que 0.")
            if record.iCreditos_totales > MAX_CREDITOS:
                raise models.ValidationError(f"Una titulación no puede tener más de {MAX_CREDITOS} créditos.")

    # Entre 1 y el máximo de cursos (igual que el curso de una asignatura)
    @api.constrains('iDuracion_cursos')
    def _check_duracion(self):
        for record in self:
            if not 1 <= record.iDuracion_cursos <= MAX_CURSOS:
                raise models.ValidationError(f"La duración debe estar entre 1 y {MAX_CURSOS} cursos.")


    @api.onchange('sCod_titulacion')
    def _onchange_codigo(self):
        if self.sCod_titulacion:
            self.sCod_titulacion = self.sCod_titulacion.replace(' ', '').upper()

    @api.onchange('name')
    def _onchange_nombre(self):
        if self.name:
            nombre = self.name.strip()
            self.name = nombre[:1].upper() + nombre[1:]