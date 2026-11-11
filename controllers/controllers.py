# -*- coding: utf-8 -*-
# from odoo import http


# class Uprofe(http.Controller):
#     @http.route('/uprofe/uprofe', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/uprofe/uprofe/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('uprofe.listing', {
#             'root': '/uprofe/uprofe',
#             'objects': http.request.env['uprofe.uprofe'].search([]),
#         })

#     @http.route('/uprofe/uprofe/objects/<model("uprofe.uprofe"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('uprofe.object', {
#             'object': obj
#         })

