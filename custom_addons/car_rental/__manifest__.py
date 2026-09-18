{
    'name': 'Car Rental',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Car Rental Management System',
    'description': """Car Rental Management System""",
    'author': 'Tersom',
    'depends': ['base','mail'],
    'data': [
        'security/car_rental_security.xml',
        'security/ir.model.access.csv',
        'views/car_rental_category_views.xml',
        'views/car_rental_vehicle_views.xml',
        'views/car_rental_order_views.xml',
        'views/res_partner_views.xml',
        'views/car_rental_menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
