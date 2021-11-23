# -*- coding: utf-8 -*-
{
    'name': "my_library",

    'summary': """
        Library Management App""",

    'description': """
        This is an App focus in to provide a management background to virtual libraries, organizing the book store in a simply way.
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '12.0.1.0.1',

    'depends': [
        'base',
        'decimal_precision'
    ],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/library_book.xml',
        'views/library_book_categ.xml',
        'views/library_book_rent.xml',
        'views/library_book_rent_wizard.xml',
        'views/library_return_wizard_form.xml',
        'data/data.xml',
        'data/demo.xml'
    ],
    'demo': [
        'data/demo.xml',
    ],
    'application': True,
}