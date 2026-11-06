# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
import re

# Curso académico con el formato 2026/2027
REGEX_CURSO = r'^(\d{4})/(\d{4})$'
PRIMER_ANIO = 2000
MAX_MB = 10  # tamaño máximo del PDF en megas
def curso_academico_actual():
    """Si estamos entre septiembre y diciembre de 2026, el inicio es 2026 y el final es 2027. Si estamos en enero del 2027,
    el inicio es 2026 y el fin 2027"""
    hoy = fields.Date.today()
    inicio = hoy.year if hoy.month >= 9 else hoy.year - 1
    return f"{inicio}/{inicio + 1}"

class GuiaDocente(models.Model):
    _name = 'uprofe.guia_docente'
    _description = 'UPROFE Guía docente'
    _order = 's_curso_academico desc, asignatura_id'

    # Una guía describe una asignatura (1,1)
    # Si se borra la asignatura, se borran sus guías (ondelete='cascade')
    
    # PK = (asignatura_id, s_curso_academico)
    asignatura_id = fields.Many2one('uprofe.asignatura', string="Asignatura", required=True, ondelete='cascade')

    s_curso_academico = fields.Char(string="Curso académico", required=True, default=lambda self: curso_academico_actual(), help="Con el formato 2026/2027")
    bin_fichero = fields.Binary(string="Fichero", required=True, help="Guía docente en PDF")
    # Odoo lo necesita para guardar el nombre del fichero al subirlo
    s_nombre_fichero = fields.Char(string="Nombre del fichero")

    # Campo calculado (no se guarda): indica si la guía es la del curso académico actual
    b_es_actual = fields.Boolean(string="Curso actual", compute='_compute_es_actual')

    # Solo puede haber una guía por asignatura y curso académico
    _sql_constraints = [
        ('asignatura_curso_unique', 'unique(asignatura_id, s_curso_academico)',
         'Esta asignatura ya tiene una guía docente para ese curso académico.'),
    ]

    # Por ejemplo "[702023] Tecnologías de Sistemas de Información (2026/2027)"
    @api.depends('asignatura_id', 's_curso_academico')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.asignatura_id.display_name or ''} ({record.s_curso_academico or ''})"

    @api.depends('s_curso_academico')
    def _compute_es_actual(self):
        actual = curso_academico_actual()
        for record in self:
            record.b_es_actual = record.s_curso_academico == actual

    # Curso académico con el formato 2026/2027 y años consecutivos
    @api.constrains('s_curso_academico')
    def _check_formato_curso(self):
        for record in self:
            coincidencia = re.match(REGEX_CURSO, (record.s_curso_academico or '').strip())
            if not coincidencia:
                raise models.ValidationError("El curso académico debe tener el formato 2026/2027.")
            if int(coincidencia.group(2)) != int(coincidencia.group(1)) + 1:
                raise models.ValidationError("Los dos años del curso académico deben ser consecutivos (por ejemplo: 2026/2027).")

    # Curso académico dentro de un rango razonable: desde 2000/2001 hasta el curso que viene
    @api.constrains('s_curso_academico')
    def _check_rango_curso(self):
        siguiente = int(curso_academico_actual()[:4]) + 1
        for record in self:
            coincidencia = re.match(REGEX_CURSO, (record.s_curso_academico or '').strip())
            if not coincidencia:
                continue  # el formato ya lo comprueba _check_formato_curso
            inicio = int(coincidencia.group(1))
            if inicio < PRIMER_ANIO:
                raise models.ValidationError(f"El curso académico no puede ser anterior a {PRIMER_ANIO}/{PRIMER_ANIO + 1}.")
            if inicio > siguiente:
                raise models.ValidationError(f"Solo se pueden crear guías hasta el curso {siguiente}/{siguiente + 1}.")

    # Fichero obligatorio.
    # Se añade 'asignatura_id' para que la validación salte también al crear la guía
    # sin fichero (igual que 'partner_id' en Persona).
    @api.constrains('bin_fichero', 'asignatura_id')
    def _check_fichero_obligatorio(self):
        for record in self:
            if not record.bin_fichero:
                raise models.ValidationError("Hay que adjuntar el fichero de la guía docente.")

    # El fichero tiene que ser un PDF: por la extensión y por el contenido
    @api.constrains('bin_fichero', 's_nombre_fichero')
    def _check_fichero_pdf(self):
        # bin_size=False: para leer el contenido del fichero y no solo su tamaño
        for record in self.with_context(bin_size=False):
            if not record.bin_fichero:
                continue  # que esté lo comprueba _check_fichero_obligatorio
            if record.s_nombre_fichero and not record.s_nombre_fichero.lower().endswith('.pdf'):
                raise models.ValidationError("La guía docente debe ser un fichero PDF.")
            # Un PDF siempre empieza por "%PDF": así se detecta aunque le hayan cambiado la extensión
            if base64.b64decode(record.bin_fichero)[:4] != b'%PDF':
                raise models.ValidationError("El fichero no es un PDF válido.")

    # Tamaño máximo del fichero
    @api.constrains('bin_fichero')
    def _check_tamano_fichero(self):
        for record in self.with_context(bin_size=False):
            if record.bin_fichero and len(base64.b64decode(record.bin_fichero)) > MAX_MB * 1024 * 1024:
                raise models.ValidationError(f"El fichero no puede ocupar más de {MAX_MB} MB.")

    # Corrige el formato del curso académico: "2026-27", "2026/27" o "2026-2027" -> "2026/2027"
    @api.onchange('s_curso_academico')
    def _onchange_curso_academico(self):
        if self.s_curso_academico:
            texto = self.s_curso_academico.strip().replace('-', '/').replace(' ', '')
            coincidencia = re.match(r'^(\d{4})/(\d{2}|\d{4})$', texto)
            if coincidencia:
                inicio = coincidencia.group(1)
                fin = coincidencia.group(2)
                if len(fin) == 2:
                    fin = inicio[:2] + fin
                self.s_curso_academico = f"{inicio}/{fin}"

    # Al elegir la asignatura de una guía nueva: si ya tiene guía del curso propuesto, se propone el curso siguiente (y se avisa) para no chocar con la guía que ya existe
    @api.onchange('asignatura_id')
    def _onchange_asignatura_id(self):
        asignatura = self.asignatura_id._origin
        coincidencia = re.match(REGEX_CURSO, self.s_curso_academico or '')
        if self._origin.id or not asignatura or not coincidencia:
            return
        existe = self.search([('asignatura_id', '=', asignatura.id),
                              ('s_curso_academico', '=', self.s_curso_academico)], limit=1)
        if existe:
            inicio = int(coincidencia.group(1)) + 1
            self.s_curso_academico = f"{inicio}/{inicio + 1}"
            return {
                'warning': {
                    'title': "La asignatura ya tiene guía",
                    'message': f"Ya existe la guía del curso {existe.s_curso_academico}. "
                               f"Se propone el curso {self.s_curso_academico}.",
                }
            }