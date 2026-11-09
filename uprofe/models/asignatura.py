# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api

MAX_CODIGO = 10
MAX_NOMBRE = 60
MAX_CURSO = 6             # un grado tiene 4 cursos, a veces hasta 6
MAX_CREDITOS = 30         # el TFG puede tener más de 6
HORAS_POR_CREDITO = 25    # 1 crédito ECTS equivale a 25-30 horas de trabajo del alumno
REGEX_CODIGO = r'^[A-Z0-9]+$'  # letras mayúsculas y números, sin espacios. Ej: 702023


class Asignatura(models.Model):
    _name = 'uprofe.asignatura'
    _description = 'UPROFE Asignatura'
    _order = 'iCurso asc, selCuatrimestre asc, name asc'

    # En los desplegables de otros modelos (Sesión, Guía docente...) se puede
    # buscar la asignatura escribiendo su nombre o su código
    _rec_names_search = ['name', 'sCod_asig']

    sCod_asig = fields.Char(string="Código", required=True, help="Código de la asignatura. Por ejemplo: 702023") # PK
    name = fields.Char(string="Nombre", required=True)
    iCurso = fields.Integer(string="Curso", required=True, default=1)
    selCuatrimestre = fields.Selection([('1', 'Primer cuatrimestre'),
                                     ('2', 'Segundo cuatrimestre'),
                                     ('anual', 'Anual')],
                                    string="Cuatrimestre", required=True, default='1')
    fCreditos = fields.Float(string="Créditos ECTS", required=True, default=6.0)
    iLimite_faltas = fields.Integer(string="Límite de faltas", default=0,
                                   help="Número máximo de faltas de asistencia permitidas")

    # Campo calculado (no se guarda) para llegar a las 5 reglas de negocio: horas de trabajo que supone la asignatura para el alumno
    fHoras_trabajo = fields.Float(string="Horas de trabajo del alumno", compute='_compute_horas_trabajo',
                                 help=f"Créditos ECTS x {HORAS_POR_CREDITO} horas")

    # Unicidad de la clave con índice en la base de datos
    _sql_constraints = [
        ('cod_asig_unique', 'unique("sCod_asig")', 'Ya existe una asignatura con este código.'),
    ]

    # Nombre que se muestra en los desplegables de otros modelos: "[702023] Tecnologías de Sistemas de Información"
    @api.depends('sCod_asig', 'name')
    def _compute_display_name(self):
        for record in self:
            if record.sCod_asig:
                record.display_name = f"[{record.sCod_asig}] {record.name or ''}"
            else:
                record.display_name = record.name

    @api.depends('fCreditos')
    def _compute_horas_trabajo(self):
        for record in self:
            record.fHoras_trabajo = record.fCreditos * HORAS_POR_CREDITO

    # Sin vacíos, máximo de caracteres y solo letras mayúsculas y números
    @api.constrains('sCod_asig')
    def _check_codigo(self):
        for record in self:
            codigo = (record.sCod_asig or '').strip()
            if not codigo:
                raise models.ValidationError("El código de la asignatura no puede estar vacío.")
            if len(codigo) > MAX_CODIGO:
                raise models.ValidationError(f"El código no puede tener más de {MAX_CODIGO} caracteres.")
            if not re.match(REGEX_CODIGO, codigo):
                raise models.ValidationError("El código solo puede contener letras mayúsculas y números, sin espacios.")

    # Sin vacíos y con máximo de caracteres
    @api.constrains('name')
    def _check_nombre(self):
        for record in self:
            nombre = (record.name or '').strip()
            if not nombre:
                raise models.ValidationError("El nombre de la asignatura no puede estar vacío.")
            if len(nombre) > MAX_NOMBRE:
                raise models.ValidationError(f"El nombre no puede tener más de {MAX_NOMBRE} caracteres.")

    # Entre 1 y el máximo de cursos de una titulación
    @api.constrains('iCurso')
    def _check_curso(self):
        for record in self:
            if not 1 <= record.iCurso <= MAX_CURSO:
                raise models.ValidationError(f"El curso debe estar entre 1 y {MAX_CURSO}.")

    # Mayores que 0, con un máximo y en múltiplos de 0,5 (3, 4,5, 6...)
    @api.constrains('fCreditos')
    def _check_creditos(self):
        for record in self:
            if record.fCreditos <= 0:
                raise models.ValidationError("Los créditos deben ser mayores que 0.")
            if record.fCreditos > MAX_CREDITOS:
                raise models.ValidationError(f"Una asignatura no puede tener más de {MAX_CREDITOS} créditos.")
            if (record.fCreditos * 2) % 1 != 0:
                raise models.ValidationError("Los créditos deben ser un múltiplo de 0,5 (por ejemplo: 4,5 o 6).")

    # No puede ser negativo
    @api.constrains('iLimite_faltas')
    def _check_limite_faltas(self):
        for record in self:
            if record.iLimite_faltas < 0:
                raise models.ValidationError("El límite de faltas no puede ser negativo.")

    # Mayúsculas y sin espacios
    @api.onchange('sCod_asig')
    def _onchange_codigo(self):
        if self.sCod_asig:
            self.sCod_asig = self.sCod_asig.replace(' ', '').upper()

    # Sin espacios sobrantes y con la primera letra en mayúscula
    @api.onchange('name')
    def _onchange_nombre(self):
        if self.name:
            nombre = self.name.strip()
            self.name = nombre[:1].upper() + nombre[1:]

    # PR Guía docente: 
    
    # Una asignatura tiene sus guías docentes (1,N)
    guia_ids = fields.One2many('uprofe.guia_docente', 'asignatura_id', string="Guías docentes")

    # La guía docente vigente es la del curso académico más reciente
    guia_actual_id = fields.Many2one('uprofe.guia_docente', string="Guía docente vigente", compute='_compute_guia_actual')

    @api.depends('guia_ids', 'guia_ids.sCurso_academico')
    def _compute_guia_actual(self):
        for record in self:
            # sorted() ordena las guías; [:1] se queda con la primera (o con ninguna si no hay)
            record.guia_actual_id = record.guia_ids.sorted('sCurso_academico', reverse=True)[:1]

   # PR Sesion: 

    # Relación del diagrama E-R: una asignatura tiene sus sesiones (1,N)
    sesion_ids = fields.One2many('uprofe.sesion', 'asignatura_id', string="Sesiones")

    # Reglas de negocio: número de sesiones y horas programadas (campos calculados, no se guardan)
    iNum_sesiones = fields.Integer(string="Número de sesiones", compute='_compute_sesiones')
    fHoras_programadas = fields.Float(string="Horas programadas", compute='_compute_sesiones')

    @api.depends('sesion_ids', 'sesion_ids.fDuracion')
    def _compute_sesiones(self):
        for record in self:
            record.iNum_sesiones = len(record.sesion_ids)
            record.fHoras_programadas = sum(record.sesion_ids.mapped('fDuracion'))
