from odoo import fields, models, api
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    _inherit = ['base.archive']
    _order = 'date_release desc, name'
    
    name = fields.Char('Title', required=True, index=True)
    isbn = fields.Char('ISBN')
    short_name = fields.Char('Short Title', translate=True, index=True)
    rec_name = 'short_name'
    notes = fields.Text('Internal Notes')
    author_ids = fields.Many2many('res.partner', string='Authors')
    
    state = fields.Selection([
            ('draft', 'Unavaliable'),
            ('avaliable', 'Avaliable'),
            ('borrowed', 'Borrowed'),
            ('lost', 'Lost')],
            'State', default="draft")

    description = fields.Html('Description', sanitize=True, strip_style=False)
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_release = fields.Date('Release Date')
    date_updated = fields.Datetime('Last Updated', copy=False)
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
    retail_price = fields.Monetary('Retail Price')
    publisher_id = fields.Many2one(
        'res.partner', 
        string='Publisher',
        ondelete='set null',
        context={},
        domain=[],
        )
    publisher_city = fields.Char(
        'Publisher City',
        related='publisher_id.city',
        readonly=True
    )
    category_id = fields.Many2one('library.book.category')
    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=False,
        compute_sudo=False,
        )
    ref_doc_id = fields.Reference(
        selection='_referenciable_models',
        string='Reference Document'
    )
    date_return = fields.Date('Date to return')
    manager_remarks = fields.Text('Manager Remarks')
    # old_edition = fields.Many2one('library.book', string='Old Edition')

    @api.model
    def _referenciable_models(self):
        models = self.env['ir.model'].search([
            ('field_id.name', '=', 'message_ids')
        ])
        return [(x.model, x.name) for x in models]
    
    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [
            ('draft', 'avaliable'),
            ('avaliable', 'borrowed'),
            ('borrowed', 'avaliable'),
            ('avaliable',   'lost'),
            ('lost', 'avaliable')]
        return (old_state, new_state) in allowed

    @api.model
    def make_avaliable(self):
        self.change_state('avaliable')

    @api.model
    def make_borrowed(self):
        self.change_state('borrowed')

    @api.model
    def make_lost(self):
        self.change_state('lost')

    def create_categories(self):
        categ1 = {
            'name': 'Child Category 1',
            'description': 'Description for Child 1'
        }
        categ2 = {
            'name': 'Child Category 1',
            'description': 'Description for Child 2'
        }
        parent_category_val = {
            'name': 'Parent Category',
            'description': 'Description for Parent Category',
            'child_ids': [
                (0, 0, categ1),
                (0, 0, categ2),
            ]
        }
        record = self.env['library.book.category'].create(parent_category_val)
        #to create multiple records in a batch, use the following line:
        # record = self.env['library.book.category'].create([categ1, categ2])
    
    @api.model
    def get_all_library_members(self):
        library_member_model = self.env['library.member']
        return library_member_model.search([])

    @api.model
    def get_author_names(self, books):
        return books.mapped('author_ids.name')

    @api.model
    def sort_books_by_date(self, books):
        return books.sorted(key='release_date', reverse=True)

    def find_books(self):
        allbooks = self.search([])
        filtered_books = self.books_with_multiple_authors(allbooks)
        logger.info('Filtered Books: %s', filtered_books)

    @api.model
    def books_with_multiple_authors(self, all_books):
        def predicate(book):
            if len(book.author_ids):
                return True
            return False
        return all_books.filter(predicate)

    @api.model
    def create(self, values):
        if not self.user_has_groups('my_library.acl_book_librarian'):
            if 'manager_remarks' in values:
                raise UserError(
                    'You are not allowed to modify '
                    'manager_remarks'
                )
        return super(LibraryBook, self).create(values)
    
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = [] if args is None else args.copy()
        if not(name == '' and operator == 'ilike'):
            args += ['|', '|',
                ('name', operator, name),
                ('isbn', operator, name),
                ('author_ids.name', operator, name)
            ]
            books_ids = self.search(args).ids
            return self.browse(books_ids).name_get()
        return super(LibraryBook, self)._name_search(
            name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    def grouped_data(self):
        data = self._get_average_cost()
        _logger.info("Grouped Data %s" % data)

    @api.model
    def _get_average_cost(self):
        grouped_result = self.read_group(
            [('cost_price', '!=', False)],
            ['category_id', 'cost_price:avg'],
            ['category_id']
        )
        return grouped_result

    @api.model
    def _update_book_price(self, category, amount_to_increase):
        category_books = self.search([('category_id', '=', category.id)])
        for book in category_books:
            book.cost_price += amount_to_increase

    @api.multi
    def write(self, values):
        if not self.user_has_groups('my_library.acl_book_librarian'):
            if 'manager_remarks' in values:
                raise UserError(
                    'You are not allowed to modify '
                    'manager_remarks'
                )
        return super(LibraryBook, self).write(values)

    @api.multi
    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (book.state, new_state)
                raise UserError(msg)
    
    @api.multi
    def change_update_date(self):
        self.ensure_one()
        self.update({
            'date_updated': fields.Datetime.now()
        })

    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            delta = today - book.date_release
            book.age_days = delta.days

    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d
    
    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        operator_map = {
            '>': '<',
            '>=': '<=',
            '<': '>',
            '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]

    @api.multi
    def name_get(self):
        result = []
        
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
            result.append((record.id, rec_name))
        
        for book in self:
            authors = book.author_ids.mapped('name')
            name = '%s (%s)' % (book.name, ', '.join(authors))
            result.append((book.id, name))
        
        return result

    @api.multi
    def find_book(self):
        domain = [
            '|',
                '&',    ('name', 'ilike', 'Book Name'),
                        ('category_id.name', 'ilike', 'Category Name'),
                '&',    ('name', 'ilike', 'Book Name 2'),
                        ('category_id.name', 'ilike', 'Category Name 2')
        ]
        books = self.search(domain)
        logger.info('Books found: %s', books)
        return True

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)', 'Book title must be unique.'),
        ('positive_page', 'CHECK(pages>0)', 'No of pages must be positive')
    ]

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past.')
    

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

class LibraryMember(models.Model):
    _name = 'library.member'
    _inherits = {'res.partner': 'partner_id'}
    partner_id = fields.Many2one('res.partner', required=True,ondelete='cascade')
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')