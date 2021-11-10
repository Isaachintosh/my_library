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
    'version': '12.0.1',

    'depends': [
        'base',
        'decimal_precision'
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/library_book.xml',
        # 'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}