from odoo import fields, models
from odoo.addons import decimal_precision as dp


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    _order = 'date_release desc, name'
    
    name = fields.Char('Title', required=True, index=True)
    short_name = fields.Char('Short Title', translate=True, index=True)
    rec_name = 'short_name'
    notes = fields.Text('Internal Notes')
    author_ids = fields.Many2many('res.partner', string='Authors')
    state = fields.Selection(
        [
            ('draft', 'Not Avaliable'),
            ('avaliable', 'Avaliable'),
            ('lost', 'Lost')
        ],
        'State', default="draft"
    )
    description = fields.Html('Description', sanitize=True, strip_style=False)
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_release = fields.Date('Release Date')
    pages = fields.Integer(
        'Number of Pages',
        groups='base.group_user',
        states={'lost': [('readonly', True)]},
        help='Total book page count',
        company_dependent=False
        )
    reader_rating = fields.Float(
        'Reader Average Rating', 
        digits=(14, 4), #Optional precision (total, decimals)
        )
    cost_price = fields.Float(
        'Book Cost',
        digits=dp.get_precision('Book Price')
        )
    currency_id = fields.Many2one('res.currency', string='Currency')
    publisher_id = fields.Many2one(
        'res.partner', 
        string='Publisher',
        ondelete='set null',
        context={},
        domain=[],
        )
    category_id = fields.Many2one('library.book.category')

def name_get(self):
    result = []
    for record in self:
        rec_name = "%s (%s)" % (record.name, record.date_release)
        result.append((record.id, rec_name))
        return result

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
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