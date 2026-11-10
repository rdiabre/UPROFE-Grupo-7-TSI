# -*- coding: utf-8 -*-

from odoo import models, fields, api

# Años permitidos para el curso académico: desde 2000/2001 hasta el curso que viene
PRIMER_ANIO = 2000

class GuiaDocente(models.Model):
    _name = 'uprofe.guia_docente'
    _description = 'UPROFE Guía docente'
    _order = 'sCurso_academico desc, asignatura_id'

    """Curso académico actual con el formato 2026/2027. Si estamos entre septiembre y diciembre de 2026,
    el curso es 2026/2027. Si estamos en enero de 2027, también es 2026/2027.
    Va antes de los campos porque se usa como valor por defecto de sCurso_academico."""
    def _curso_actual(self):
        hoy = fields.Date.context_today(self)
        if hoy.month >= 9:
            inicio = hoy.year
        else:
            inicio = hoy.year - 1
        return f"{inicio}/{inicio + 1}"

    # PK = (asignatura_id, sCurso_academico)
    # Una guía describe una asignatura (1,1). Si se borra la asignatura, se borran sus guías
    asignatura_id = fields.Many2one('uprofe.asignatura', string="Asignatura", required=True, ondelete='cascade')
    sCurso_academico = fields.Char(string="Curso académico", required=True, default=_curso_actual, help="Con el formato 2026/2027")
    binFichero = fields.Binary(string="Fichero", required=True, help="Guía docente en PDF")
    # Nombre del fichero subido (la vista lo rellena con filename="sNombre_fichero"). Sirve para comprobar que es .pdf
    sNombre_fichero = fields.Char(string="Nombre del fichero")

    # Campos calculados
    # Nombre que se muestra al elegir la guía en otros modelos: "702023 (2026/2027)"
    name = fields.Char(string="Guía docente", compute='_compute_name')
    # Si la guía es la del curso académico actual (no se guarda)
    bEs_actual = fields.Boolean(string="Curso actual", compute='_compute_es_actual')

    # Solo puede haber una guía por asignatura y curso académico
    _sql_constraints = [
        ('asignatura_curso_unique', 'unique(asignatura_id, "sCurso_academico")',
         'Esta asignatura ya tiene una guía docente para ese curso académico.'),
    ]

    @api.depends('asignatura_id', 'sCurso_academico')
    def _compute_name(self):
        for record in self:
            codigo = record.asignatura_id.sCod_asig
            if not codigo:
                codigo = ''
            curso = record.sCurso_academico
            if not curso:
                curso = ''
            record.name = f"{codigo} ({curso})"

    @api.depends('sCurso_academico')
    def _compute_es_actual(self):
        for record in self:
            record.bEs_actual = record.sCurso_academico == record._curso_actual()

    # Curso académico: formato 2026/2027, años consecutivos y dentro del rango permitido
    @api.constrains('sCurso_academico')
    def _check_curso(self):
        for record in self:
            curso = record.sCurso_academico
            if not curso or curso.strip() == '':
                raise models.ValidationError("El curso académico no puede estar vacío.")
            curso = curso.strip()
            # "2026/2027": 9 caracteres, 4 cifras, una barra y 4 cifras
            if len(curso) != 9 or curso[4] != '/' or not curso[:4].isdigit() or not curso[5:].isdigit():
                raise models.ValidationError("El curso académico debe tener el formato 2026/2027.")
            inicio = int(curso[:4])
            fin = int(curso[5:])
            if fin != inicio + 1:
                raise models.ValidationError("Los dos años del curso académico deben ser consecutivos (por ejemplo: 2026/2027).")
            siguiente = int(record._curso_actual()[:4]) + 1
            if inicio < PRIMER_ANIO:
                raise models.ValidationError(f"El curso académico no puede ser anterior a {PRIMER_ANIO}/{PRIMER_ANIO + 1}.")
            if inicio > siguiente:
                raise models.ValidationError(f"Solo se pueden crear guías hasta el curso {siguiente}/{siguiente + 1}.")

    # Fichero obligatorio. Se añade 'asignatura_id' para que la validación salte
    # también al crear la guía sin fichero (igual que 'partner_id' en Persona)
    @api.constrains('binFichero', 'asignatura_id')
    def _check_fichero(self):
        for record in self:
            if not record.binFichero:
                raise models.ValidationError("Hay que adjuntar el fichero de la guía docente.")

    # El fichero tiene que terminar en .pdf (lower(): también vale .PDF)
    @api.constrains('sNombre_fichero')
    def _check_pdf(self):
        for record in self:
            if record.sNombre_fichero and not record.sNombre_fichero.lower().endswith('.pdf'):
                raise models.ValidationError("La guía docente debe ser un fichero PDF.")

    # Curso académico sin espacios y con barra: "2026 - 2027" -> "2026/2027"
    @api.onchange('sCurso_academico')
    def _onchange_curso_academico(self):
        if self.sCurso_academico:
            self.sCurso_academico = self.sCurso_academico.replace(' ', '').replace('-', '/')