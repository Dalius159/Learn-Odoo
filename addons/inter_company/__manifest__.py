{
    'name': 'Intercompany Transfers',
    'version': '1.2',
    'author': 'Rodanus',
    'depends': ['purchase','sale','sale_management','stock'],
    'data': [
        'data/ir.model.access.csv',
        'views/report_wizard.xml',
        'views/stock_quant_period.xml',
    ],
    'installable': True,
}