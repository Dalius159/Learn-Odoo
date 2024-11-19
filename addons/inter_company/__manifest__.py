{
    'name': 'Intercompany Transfers',
    'version': '1.2',
    'author': 'Rodanus',
    'depends': ['purchase','sale','sale_management','stock'],
    'data': [
        'data/ir.model.access.csv',
        'views/stock_report_wizard_view.xml',
        'views/stock_quant_period_view.xml',
    ],
    'installable': True,
}