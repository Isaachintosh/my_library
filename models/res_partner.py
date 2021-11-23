from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'name'
    
    published_book_ids = fields.One2many(
        'library.book',
        'publisher_id',
        string='Published Books'
    )

    authored_book_ids = fields.Many2many(
        'library.book',
        string='Authored Books',
        # relation='library_book_res_partner_rel'
    )
    count_books = fields.Integer(
        'Number of Authored Books',
        compute='_compute_count_books'
        )
    
    @api.depends('authored_books_ids')
    def _compute_cout_books(self):
        for r in self:
            r.count_books = len (r.authored_books_ids)