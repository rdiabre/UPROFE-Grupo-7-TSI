# -*- coding: utf-8 -*-

import base64
from odoo import models, fields, api

# Primeros bytes de una imagen PNG y de una JPEG
INICIO_PNG = b'\x89PNG'
INICIO_JPEG = b'\xff\xd8'

class Acta(models.Model):
    _name = 'uprofe.acta'
    _description = 'UPROFE Acta'
    _order = 'iNum_acta desc'

    # PK
    iNum_acta = fields.Integer(string="Número de acta", required=True, copy=False, default=lambda self: self._siguiente_numero())
    # Firma del profesor: se dibuja en el formulario (signature). Un acta firmada es un acta publicada: sus notas pasan a los expedientes.
    binFirma = fields.Binary(string="Firma del profesor", copy=False)

    # Relación del diagrama E-R: un acta contiene una o varias líneas (1,N)
    linea_ids = fields.One2many('uprofe.linea_acta', 'acta_id', string="Líneas del acta")

    # Campos calculados a partir de la firma y de las líneas
    bPublicada = fields.Boolean(string="Publicada", compute='_compute_publicada', store=True)
    convocatoria_id = fields.Many2one('uprofe.convocatoria_asignatura', string="Convocatoria", compute='_compute_convocatoria', store=True)
    asignatura_id = fields.Many2one('uprofe.asignatura', string="Asignatura", related='convocatoria_id.asignatura_id', store=True)
    iNum_lineas = fields.Integer(string="Alumnos", compute='_compute_resumen', store=True)
    iNum_aprobados = fields.Integer(string="Aprobados", compute='_compute_resumen', store=True)
    iNum_suspensos = fields.Integer(string="Suspensos", compute='_compute_resumen', store=True)
    fNota_media = fields.Float(string="Nota media", compute='_compute_resumen', store=True, digits=(4, 2), aggregator='avg')

    _sql_constraints = [
        ('num_acta_unique', 'unique("iNum_acta")', 'Ya existe un acta con este número.'),
    ]

    # Número de acta: el siguiente al último que existe
    def _siguiente_numero(self):
        ultima = self.search([], order='iNum_acta desc', limit=1)
        return ultima.iNum_acta + 1 if ultima else 1

    # Nombre que se muestra: "Acta 7 – [702023] Tecnologías de Sistemas de Información"
    @api.depends('iNum_acta', 'asignatura_id')
    def _compute_display_name(self):
        for record in self:
            nombre = f"Acta {record.iNum_acta}"
            if record.asignatura_id:
                nombre += f" - {record.asignatura_id.display_name}"
            record.display_name = nombre

    # Un acta está publicada cuando el profesor la firma
    @api.depends('binFirma')
    def _compute_publicada(self):
        for record in self:
            record.bPublicada = bool(record.binFirma)

    # La convocatoria del acta es la de sus líneas (todas tienen la misma)
    @api.depends('linea_ids.convocatoria_id')
    def _compute_convocatoria(self):
        for record in self:
            record.convocatoria_id = record.linea_ids[:1].convocatoria_id

    # Resumen del acta: alumnos, aprobados, suspensos y nota media
    @api.depends('linea_ids.fNota', 'linea_ids.bAprobada')
    def _compute_resumen(self):
        for record in self:
            notas = record.linea_ids.mapped('fNota')
            record.iNum_lineas = len(record.linea_ids)
            record.iNum_aprobados = len(record.linea_ids.filtered('bAprobada'))
            record.iNum_suspensos = record.iNum_lineas - record.iNum_aprobados
            record.fNota_media = sum(notas) / len(notas) if notas else 0

    # Número de acta mayor que 0
    @api.constrains('iNum_acta')
    def _check_num_acta(self):
        for record in self:
            if record.iNum_acta <= 0:
                raise models.ValidationError("El número de acta debe ser mayor que 0.")

    # Solo se puede firmar (publicar) un acta que tenga líneas
    @api.constrains('binFirma', 'linea_ids')
    def _check_firma_con_lineas(self):
        for record in self:
            if record.binFirma and not record.linea_ids:
                raise models.ValidationError("No se puede firmar un acta sin alumnos.")

    # La firma tiene que ser una imagen png o jpeg
    @api.constrains('binFirma')
    def _check_firma_imagen(self):
        # bin_size=False: para leer el contenido de la firma y no solo su tamaño
        for record in self.with_context(bin_size=False):
            if record.binFirma:
                contenido = base64.b64decode(record.binFirma)
                if not (contenido.startswith(INICIO_PNG) or contenido.startswith(INICIO_JPEG)):
                    raise models.ValidationError("La firma debe ser una imagen (PNG o JPEG).")

    # No se puede firmar un acta antes de que se celebre el examen de su convocatoria
    @api.constrains('binFirma')
    def _check_firma_fecha_convocatoria(self):
        hoy = fields.Date.context_today(self)
        for record in self:
            fecha_examen = record.convocatoria_id.dFecha
            if record.binFirma and fecha_examen and fecha_examen > hoy:
                raise models.ValidationError(f"No se puede firmar el acta antes de la fecha del examen "
                                      f"({fecha_examen.strftime('%d/%m/%Y')}).")

    # El acta tiene una sola firma: para firmarla, todas sus notas tienen que estar publicadas por el mismo profesor (el que firma)
    @api.constrains('binFirma', 'linea_ids')
    def _check_firma_mismo_profesor(self):
        for record in self:
            if record.binFirma and len(record.linea_ids.mapped('profesor_id')) > 1:
                raise models.ValidationError("Para firmar el acta, todas sus notas deben ser del mismo profesor.")

    # Al añadir líneas en el formulario: se numeran seguidas y las nuevas toman la convocatoria y el profesor de la primera línea, para no tener que repetirlos
    @api.onchange('linea_ids')
    def _onchange_linea_ids(self):
        primera = self.linea_ids[:1]
        for numero, linea in enumerate(self.linea_ids, start=1):
            linea.iNum_linea = numero
            if not linea.convocatoria_id:
                linea.convocatoria_id = primera.convocatoria_id
            if not linea.profesor_id:
                linea.profesor_id = primera.profesor_id
