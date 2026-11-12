# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api

MAX_NUM_TF = 20
MAX_TITULO = 200
MAX_RESUMEN = 2000
#letras mayúsculas, números y guiones, sin espacios.
REGEX_NUM_TF = r'^[A-Z0-9-]+$'
#repito las reglas de 'plan de estudio' para no depender de ese archivo
REGEX_CURSO = r'^(\d{4})/(\d{4})$'
PRIMER_ANIO = 2000  #el curso más antiguo permitido es 2000/2001


class TrabajoFinal(models.Model):
    _name = 'uprofe.trabajo_final'
    _description = 'UPROFE Trabajo final'
    _rec_name = 'sNum_tf'
    _order = 'sCurso_academico desc, sNum_tf asc'

    """Curso académico actual con el formato 2026/2027: de septiembre a diciembre es el año en curso / el siguiente, y de
    enero a agosto es el año anterior / el actual. Va antes de los campos porque se usa como valor por defecto."""
    def _curso_actual(self):
        hoy = fields.Date.context_today(self)
        inicio = hoy.year if hoy.month >= 9 else hoy.year - 1
        return f"{inicio}/{inicio + 1}"

    
    sNum_tf = fields.Char(string="Nº de trabajo final", size=MAX_NUM_TF, required=True, copy=False,help="Identificador del trabajo final.")  
    sTitulo = fields.Char(string="Título", required=True)
    sResumen = fields.Text(string="Resumen")  #opcional: en el diagrama no es clave
    sCurso_academico = fields.Char(string="Curso académico", required=True, default=_curso_actual, help="Con el formato 2026/2027")
    fCalificacion = fields.Float(string="Calificación", required=True, default=0, help="Nota del 0 al 10 del trabajo final. Por defecto, 0")

    #debería poner ondelete='restrict' para que no se pueda borrar un plan de estudio que tenga un trabajo final asociado?
    plan_estudio_id = fields.Many2one('uprofe.plan_estudio', string="Plan de estudio", required=True)

    #cada trabajo tiene un tutor y un profesor puede tutorizar varios
    profesor_id = fields.Many2one('uprofe.profesor', string="Tutor", required=True, ondelete='restrict')

    #cada trabajo lo hace un alumno y un alumno puede hacer varios (por ejemplo: doble grado)
    alumno_id = fields.Many2one('uprofe.alumno', string="Alumno", required=True, ondelete='restrict')

    #titulación del trabajo, sacada de su plan de estudio. Se guarda (store) para poder filtrar y agrupar por ella
    titulacion_id = fields.Many2one(related='plan_estudio_id.titulacion_id', string="Titulación", store=True)

    #un trabajo tiene como mucho una defensa y cada defensa es de un solo trabajo.
    #DESCOMENTAR cuando defensa_tf esté en main. El campo inverso es
    #defensa_tf.trabajo_final_id (Many2one, required=True y con unique en su _sql_constraints) y, como mucho, habrá una:
    #defensa_tf_ids = fields.One2many('uprofe.defensa_tf', 'trabajo_final_id', string="Defensa")

    _sql_constraints = [
        #impide que dos trabajos finales tengan el mismo número
        ('num_tf_unique', 'unique("sNum_tf")', 'Ya existe un trabajo final con este número.'),
        #un alumno no puede tener dos trabajos finales del mismo plan en el mismo curso académico
        ('alumno_plan_curso_unique', 'unique(alumno_id, plan_estudio_id, "sCurso_academico")',
         'Este alumno ya tiene un trabajo final de este plan de estudio en ese curso académico.'),
    ]

    #nombre que se muestra en los desplegables de otros modelos: "TF-2026-001 · Título del trabajo"
    @api.depends('sNum_tf', 'sTitulo')
    def _compute_display_name(self):
        for record in self:
            if record.sNum_tf:
                record.display_name = f"{record.sNum_tf} · {record.sTitulo or ''}"
            else:  #si no hay número (registro nuevo), se muestra el título
                record.display_name = record.sTitulo or ''

    #número: no vacío, máximo de caracteres y solo mayúsculas, números y guiones
    @api.constrains('sNum_tf')
    def _check_num_tf(self):
        for record in self:
            numero = (record.sNum_tf or '').strip()
            if not numero:
                raise models.ValidationError("El número del trabajo final no puede estar vacío.")
            if len(numero) > MAX_NUM_TF:
                raise models.ValidationError(f"El número no puede tener más de {MAX_NUM_TF} caracteres.")
            if not re.match(REGEX_NUM_TF, numero):
                raise models.ValidationError("El número solo puede contener letras mayúsculas, números y guiones, sin espacios.")

    #título: no vacío, máximo de caracteres
    @api.constrains('sTitulo')
    def _check_titulo(self):
        for record in self:
            titulo = (record.sTitulo or '').strip()
            if not titulo:
                raise models.ValidationError("El título del trabajo final no puede estar vacío.")
            if len(titulo) > MAX_TITULO:
                raise models.ValidationError(f"El título no puede tener más de {MAX_TITULO} caracteres.")

    #resumen: es opcional, pero si se rellena no puede ser solo espacios ni pasarse de largo
    @api.constrains('sResumen')
    def _check_resumen(self):
        for record in self:
            if record.sResumen:
                resumen = record.sResumen.strip()
                if not resumen:
                    raise models.ValidationError("El resumen no puede estar vacío.")
                if len(resumen) > MAX_RESUMEN:
                    raise models.ValidationError(f"El resumen no puede tener más de {MAX_RESUMEN} caracteres.")

    #curso académico con el formato 2026/2027 y años consecutivos
    @api.constrains('sCurso_academico')
    def _check_formato_curso(self):
        for record in self:
            coincidencia = re.match(REGEX_CURSO, (record.sCurso_academico or '').strip())
            if not coincidencia:
                raise models.ValidationError("El curso académico debe tener el formato 2026/2027.")
            if int(coincidencia.group(2)) != int(coincidencia.group(1)) + 1:
                raise models.ValidationError("Los dos años del curso académico deben ser consecutivos (por ejemplo: 2026/2027).")

    #curso dentro de un rango razonable: desde 2000/2001 hasta el curso que viene
    @api.constrains('sCurso_academico')
    def _check_rango_curso(self):
        for record in self:
            coincidencia = re.match(REGEX_CURSO, (record.sCurso_academico or '').strip())
            if not coincidencia:
                continue  #el formato ya lo comprueba _check_formato_curso
            siguiente = int(record._curso_actual()[:4]) + 1
            inicio = int(coincidencia.group(1))
            if inicio < PRIMER_ANIO:
                raise models.ValidationError(f"El curso académico no puede ser anterior a {PRIMER_ANIO}/{PRIMER_ANIO + 1}.")
            if inicio > siguiente:
                raise models.ValidationError(f"Solo se pueden registrar trabajos hasta el curso {siguiente}/{siguiente + 1}.")

    #regla entre dos campos: el trabajo no puede ser de un curso anterior al del plan de estudio al que pertenece
    #(se incluye plan_estudio_id para que salte también al cambiar de plan)
    @api.constrains('sCurso_academico', 'plan_estudio_id')
    def _check_curso_vs_plan(self):
        for record in self:
            trabajo = re.match(REGEX_CURSO, (record.sCurso_academico or '').strip())
            plan = re.match(REGEX_CURSO, record.plan_estudio_id.sCurso_academico or '')
            if trabajo and plan and int(trabajo.group(1)) < int(plan.group(1)):
                raise models.ValidationError(
                    f"El trabajo es del curso {record.sCurso_academico}, anterior al del plan de estudio "
                    f"({record.plan_estudio_id.sCurso_academico}).")

    # ONCHANGE (solo en el formulario; siempre con "if": también se ejecutan con el campo vacío)
    #número en mayúsculas y sin espacios
    @api.onchange('sNum_tf')
    def _onchange_num_tf(self):
        if self.sNum_tf:
            self.sNum_tf = self.sNum_tf.replace(' ', '').upper()

    #título sin espacios sobrantes y con la primera letra en mayúscula, el resto queda igual
    @api.onchange('sTitulo')
    def _onchange_titulo(self):
        if self.sTitulo:
            titulo = self.sTitulo.strip()
            self.sTitulo = titulo[:1].upper() + titulo[1:]

    #resumen sin espacios sobrantes
    @api.onchange('sResumen')
    def _onchange_resumen(self):
        if self.sResumen:
            self.sResumen = self.sResumen.strip()

    #corrige el formato del curso académico, como en 'plan de estudio'
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

    #al elegir el plan de estudio: si el curso del trabajo está vacío o es anterior al del plan, se pone el del plan y se avisa
    @api.onchange('plan_estudio_id')
    def _onchange_plan_estudio_id(self):
        plan = self.plan_estudio_id
        plan_curso = re.match(REGEX_CURSO, plan.sCurso_academico or '') if plan else None
        if not plan_curso:
            return
        trabajo_curso = re.match(REGEX_CURSO, self.sCurso_academico or '')
        if not trabajo_curso:
            self.sCurso_academico = plan.sCurso_academico
        elif int(trabajo_curso.group(1)) < int(plan_curso.group(1)):
            anterior = self.sCurso_academico
            self.sCurso_academico = plan.sCurso_academico
            return {
                'warning': {
                    'title': "Curso anterior al del plan",
                    'message': f"El curso {anterior} es anterior al del plan de estudio. "
                               f"Se ha puesto el curso {plan.sCurso_academico}.",
                }
            }