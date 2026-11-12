# -*- coding: utf-8 -*-
import base64
import re

from odoo import models, fields, api

REGEX_CURSO = r'^(\d{4})/(\d{4})$'
PRIMER_ANIO = 2000
MAX_MB = 10  #tamaño máximo del PDF en megas

class PlanEstudio(models.Model):
    _name = 'uprofe.plan_estudio'
    _description = 'Plan de estudio'
    _order = 'sCurso_academico desc, titulacion_id'

    def _curso_actual(self):
        hoy = fields.Date.context_today(self)
        if hoy.month >= 9:
            inicio = hoy.year
        else:
            inicio = hoy.year - 1
        return f"{inicio}/{inicio+1}"

    #plan de estudio es entidad débil porque no existe sin titulación y su PK es compuesta.
    #el plan pertenece a UNA titulación (required=True) y, si se borra la titulación, se borran sus planes
    titulacion_id = fields.Many2one('uprofe.titulacion', string="Titulación", required=True, ondelete='cascade')

    sCurso_academico = fields.Char(string="Curso académico", required=True, default=_curso_actual, help="Con el formato 2026/2027")

    binFichero = fields.Binary(string="Fichero", help="Plan de estudio en PDF")
    sNombre_fichero = fields.Char(string="Nombre del fichero")

    #plan de estudio tiene una relación de tres entidades con asignatura y convocatoria asignatura. La asignatura se asocia a través de su convocatoria
    #y por cada plan y asignatura hay 1 o 2 convos (esa regla va en otros modelos)
    #convocatoria_asignatura_ids = fields.One2many('uprofe.convocatoria_asignatura', 'plan_estudio_id', string="Asignaturas y convocatorias")

    #un plan puede tener cero o muchos trabajos finales
    trabajo_final_ids = fields.One2many('uprofe.trabajo_final', 'plan_estudio_id', string="Trabajos finales")

    #Campo calculado que indica si el plan es el del curso académico actual
    bEs_actual = fields.Boolean(string="Curso actual", compute='_compute_es_actual')

    #solo puede haber un plan por titulación y curso académico
    _sql_constraints = [
        ('titulacion_curso_unique', 'unique("titulacion_id", "sCurso_academico")',
         'Esta titulación ya tiene un plan de estudio para ese curso académico.'),
    ]

    @api.depends('titulacion_id', 'sCurso_academico')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.titulacion_id.display_name or ''} ({record.sCurso_academico or ''})"

    @api.depends('sCurso_academico')
    def _compute_es_actual(self):
        for record in self:
            record.bEs_actual = record.sCurso_academico == record._curso_actual()

    #curso académico con el formato 2026/2027 y comprobar que los años sean consecutivos
    @api.constrains('sCurso_academico')
    def _check_formato_curso(self):
        for record in self:
            coincidencia = re.match(REGEX_CURSO, (record.sCurso_academico or '').strip())
            if not coincidencia:
                raise models.ValidationError("El curso académico debe tener el formato 2026/2027.")
            if int(coincidencia.group(2)) != int(coincidencia.group(1)) + 1:
                raise models.ValidationError("Los dos años del curso académico deben ser consecutivos (por ejemplo: 2026/2027).")

    #comprobamos que el curso académico introducido sea de este siglo por lo menos xd, y no mayor al del año que viene
    @api.constrains('sCurso_academico')
    def _check_rango_curso(self):
        for record in self:
            coincidencia = re.match(REGEX_CURSO, (record.sCurso_academico or '').strip())
            if not coincidencia:
                continue  # el formato ya lo comprueba _check_formato_curso
            siguiente = int(record._curso_actual()[:4]) + 1
            inicio = int(coincidencia.group(1))
            if inicio < PRIMER_ANIO:
                raise models.ValidationError(f"El curso académico no puede ser anterior a {PRIMER_ANIO}/{PRIMER_ANIO + 1}.")
            if inicio > siguiente:
                raise models.ValidationError(f"Solo se pueden crear planes hasta el curso {siguiente}/{siguiente + 1}.")

    #El fichero es opcional, pero si se sube tiene que ser un PDF: por la extensión y por el contenido (la verdad que le he preguntao a la IA)
    @api.constrains('binFichero', 'sNombre_fichero')
    def _check_fichero_pdf(self):
        # bin_size=False: para leer el contenido del fichero y no solo su tamaño
        for record in self.with_context(bin_size=False):
            if not record.binFichero:
                continue  # sin fichero no hay nada que comprobar
            if record.sNombre_fichero and not record.sNombre_fichero.lower().endswith('.pdf'):
                raise models.ValidationError("El plan de estudio debe ser un fichero PDF.")
            # Un PDF siempre empieza por "%PDF": así se detecta aunque le hayan cambiado la extensión
            if base64.b64decode(record.binFichero)[:4] != b'%PDF':
                raise models.ValidationError("El fichero no es un PDF válido.")

    #Tamaño máximo del fichero
    @api.constrains('binFichero')
    def _check_tamano_fichero(self):
        for record in self.with_context(bin_size=False):
            if record.binFichero and len(base64.b64decode(record.binFichero)) > MAX_MB * 1024 * 1024:
                raise models.ValidationError(f"El fichero no puede ocupar más de {MAX_MB} MB.")

    #Corrige el formato del curso académico para que sea "2026/2027"
    @api.onchange('sCurso_academico')
    def _onchange_curso_academico(self):
        if self.sCurso_academico:
            texto = self.sCurso_academico.strip().replace('-', '/').replace(' ', '')
            coincidencia = re.match(r'^(\d{4})/(\d{2}|\d{4})$', texto)
            if coincidencia:
                inicio = coincidencia.group(1)
                fin = coincidencia.group(2)
                if len(fin) == 2:
                    fin = inicio[:2] + fin
                self.sCurso_academico = f"{inicio}/{fin}"

    # Al elegir la titulación de un plan nuevo: si ya tiene plan del curso propuesto, se propone el curso
    # siguiente (y se avisa) para no chocar con el plan que ya existe.
    # self._origin.id es False si todavía no existe en la base de datos (solo se entra al crear).
    @api.onchange('titulacion_id')
    def _onchange_titulacion_id(self):
        titulacion = self.titulacion_id._origin
        coincidencia = re.match(REGEX_CURSO, self.sCurso_academico or '')
        if self._origin.id or not titulacion or not coincidencia:
            return
        existe = self.search([('titulacion_id', '=', titulacion.id),
                              ('sCurso_academico', '=', self.sCurso_academico)], limit=1)
        if existe:
            inicio = int(coincidencia.group(1)) + 1
            self.sCurso_academico = f"{inicio}/{inicio + 1}"
            return {
                'warning': {
                    'title': "La titulación ya tiene plan",
                    'message': f"Ya existe el plan del curso {existe.sCurso_academico}. "
                               f"Se propone el curso {self.sCurso_academico}.",
                }
            }