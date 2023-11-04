# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo import Command
from colorama import Fore
from datetime import datetime, date
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError

# #############################################################################
class SdPayanehNaftiReportContractDaily(models.TransientModel):
    _name = 'sd_payaneh_nafti.report.contract_daily'
    _description = 'Contract Daily Report Wizard'

    registration_no = fields.Many2one('sd_payaneh_nafti.contract_registration', required=True,)

    # report_date = fields.Date(required=True, default=lambda self: date.today() )
    # report_date = fields.Date(required=True, default=lambda self: datetime.strptime('2023-07-17', '%Y-%m-%d').date() )
    report_date = fields.Date(required=True, default=lambda self: datetime.today().date())
    calendar = fields.Selection([('fa_IR', 'Persian'), ('en_US', 'Gregorian')],
                                default=lambda self: 'fa_IR' if self.env.context.get('lang') == 'fa_IR' else 'en_US')
    payaneh_agent = fields.Char(required=True, default='payaneh_agent')
    observe_agent = fields.Char(required=True, default='observe_agent')
    buyer_agent = fields.Char(required=True, default='buyer_agent')
    # #############################################################################
    def cargo_document_report(self):
        read_form = self.read()[0]
        data = {'form_data': read_form}
        return self.env.ref('sd_payaneh_nafti.contract_daily_report').report_action(self, data=data)

    # @api.depends('report_date')
    # @api.onchange('report_date')
    # def registration_default(self):
    #     regs = self.registration_no.search([('loading_date', '=', self.report_date)])
    #     return
