{
    'name': 'Discount Program',
    'version': '1.2',
    'author': 'Rodanus',
    'depends': ['base', 'purchase','sale','sale_management','website_sale','website'],
    'data': [
        'security/groups.xml',
        'security/promotional_code_security.xml',
        'security/ir.model.access.csv',
        'views/promotional_code.xml',
        'views/sale_order.xml',
        'views/mkm_mass_creation_wizard.xml',
        'views/menu.xml',
    ],
    'installable': True,
}