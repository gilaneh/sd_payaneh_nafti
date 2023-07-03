# -*- coding: utf-8 -*-
{
    'name': "sd_payaneh_nafti",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "Arash Homayounfar",
    'website': "https://gilaneh.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Service Desk/Service Desk',
    'application': True,
    'version': '1.0.6',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'mail'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/base_info.xml',
        'views/contract_info.xml',
        'views/contract_registration.xml',
        'views/input_info.xml',
        # 'views/anomaly.xml',
        # 'views/permit.xml',
        # 'views/weather.xml',
        # 'views/drill.xml',
        # 'views/training.xml',
        # 'data/training_data.xml',
        # 'views/personnel.xml',
        # 'views/incident.xml',
        # 'views/project.xml',
        # 'views/actions.xml',
        'views/templates.xml',
        'report/loading_permit_report_template.xml',
        'report/loading_permit_report.xml',
        'wizard/loading_permit_report_wizard.xml',

    ],
    'assets': {
        # 'website.assets_editor': [
        #     'static/src/**/*',
        # ],

        'web.assets_backend': [

            'sd_payaneh_nafti/static/src/css/style.scss',
            # 'sd_payaneh_nafti/static/src/js/website_form_sd_payaneh_nafti.js'
        ],
        'web.report_assets_common': [

            'sd_payaneh_nafti/static/src/css/report_styles.css',
            # 'sd_payaneh_nafti/static/src/js/website_form_sd_payaneh_nafti.js'
        ],

    },

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',

}
