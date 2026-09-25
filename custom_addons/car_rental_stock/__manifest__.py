{
    'name': 'Car Rental - Stock Bridge',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Rental accessories inventory tracking',
    'author': 'Tersom',
    'depends': ['car_rental', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/car_rental_order_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
