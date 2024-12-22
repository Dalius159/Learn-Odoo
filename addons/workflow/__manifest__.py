{
    'name': 'Workflow Management',
    'version': '1.0',
    'author': 'Rodanus',
    'category': 'Tools',
    'summary': 'Custom Workflow Management for Odoo',
    'depends': ['base','web'],
    'data': [
        'security/ir.model.access.csv',
        'views/workflow_views.xml',
        'views/custom_state_record_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'web/static/src/views/fields/statusbar/statusbar_field.scss',
            # 'web/static/src/views/fields/statusbar/statusbar_field.variables.scss',
            'workflow/static/src/components/*'
            
            # 'workflow/static/src/fields/custom_status_bar.xml',
            # 'workflow/static/src/fields/custom_status_bar.js',
            # 'workflow/static/src/form/custom_status_bar_buttons.xml',
            # 'workflow/static/src/form/custom_status_bar_buttons.js',
        ],
    },
    'installable': True,
    'application': False,
}
