# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class estado_convenio(models.Model):
    _name= 'uprofe.estado_convenio'
    _description = 'Estados de convenio'
    _order = 'name asc'
    
     