from odoo import models, fields, api


class LibraryRentWizard(models.TransientModel):
    _name = 'library.rent.wizard'

    borrower_id = fields.Many2one('res.partner', string='Borrower')
    book_ids = fields.Many2many('library.book', string='Books')

    def add_book_rents(self):
        self.ensure_one()
        rentModel = self.env['library.book.rent']
        for book in self.book_ids:
            rentModel.create({
                'borrower_id': self.borrower_id.id,
                'book_id': book.id
            })
        members = self.mapped('borrower_id')
        action = members.get_formview_action()
        if len(borrowers.ids) > 1:
            action['domain'] = [('id', 'in', tuple(members.ids))]
            action['view_mode'] = 'tree,form'
        return action

    def books_returns(self):
        loan = self.env['library.book.rent']
        for rec in self:
            loans = loan.search(
                [('state', '=', 'ongoing'),
                ('book_id', '=', rec.book_ids.id),
                ('borrower_id', '=', rec.borrower_id.id)]
            )
            for loan in loans:
                loan.book_return

    @api.onchange('borrower_id')
    def onchange_member(self):
        rentModel = self.env['library.book.rent']
        books_on_rent = rentModel.search(
            [('state', '=', 'ongoing'),
            ('borrower_id', '=', self.borrower_id.id)]
        )
        self.book_ids = books_on_rent.mapped('book_id')
        result = {
            'domain': {
                'book_ids': [
                    ('id', 'in', self.book_ids.ids)
                ]
            }
        }
        late_books = [
            ('id', 'in', books_on_rent.ids),
            ('expected_return_date', '<', fields.Date.today())
        ]
        if late_books:
            message = ('Warn the member that the following books are late:\n')
            titles = late_books.mapped('book_id.name')
            result['warning'] = {
                'title': 'Late books',
                'message': message + '\n'.join(titles)
            }
            return result