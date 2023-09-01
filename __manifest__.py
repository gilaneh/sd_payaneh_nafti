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
    # for the full list
    'category': 'Service Desk/Service Desk',
    'application': True,
    'version': '1.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'mail'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/settings.xml',
        'views/base_info.xml',
        'views/meter_data.xml',
        'views/buyers.xml',
        'views/contractors.xml',
        'views/contract_number.xml',
        'views/destinations.xml',
        'views/signers.xml',
        'views/contract_info.xml',
        'views/contract_registration.xml',
        'views/input_info.xml',
        'views/templates.xml',
        'report/loading_permit_report_template.xml',
        'report/loading_permit_report.xml',
        'wizard/loading_permit_report_wizard.xml',
        'report/meter_report_template.xml',
        'report/meter_report.xml',
        'wizard/meter_report_wizard.xml',
        'report/cargo_document_report_template.xml',
        'report/cargo_document_report.xml',
        'wizard/cargo_document_report_wizard.xml',
        'report/contract_daily_report_template.xml',
        'report/contract_daily_report.xml',
        'wizard/contract_daily_report_wizard.xml',
        'data/registration_sequence.xml',
        'data/input_sequence.xml',
        'data/cargo_types_data.xml',

    ],
    'assets': {
        # 'website.assets_editor': [
        #     'static/src/**/*',
        # ],

        'web.assets_backend': [

            'sd_payaneh_nafti/static/src/css/style.scss',
            'sd_payaneh_nafti/static/src/js/o_field_x2many_list_row_add_none.js'
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
