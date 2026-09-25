{
    'name': 'Car Rental - Accounting Bridge',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Integrasi Car Rental dengan Invoicing',
    'author': 'Tersom',
    'depends': ['car_rental','account'],
    'data': [
        'views/car_rental_order_views.xml',
        'views/account_move.xml'
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
