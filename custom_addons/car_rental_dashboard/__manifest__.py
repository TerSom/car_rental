{
    'name': 'Car Rental Dashboard',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Car Rental Operations Dashboard',
    'depends': ['car_rental', 'car_rental_account', 'car_rental_stock'],
    'data': [
        'views/car_rental_dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'car_rental_dashboard/static/src/js/car_rental_dashboard.js',
            'car_rental_dashboard/static/src/xml/car_rental_dashboard.xml',
            'car_rental_dashboard/static/src/scss/car_rental_dashboard.scss',
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
