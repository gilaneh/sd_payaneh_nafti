# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo import Command
from colorama import Fore
from datetime import datetime, date
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError

# #############################################################################
class SdPayanehNaftiReportMeterReport(models.TransientModel):
    _name = 'sd_payaneh_nafti.report.meter_report'
    _description = 'Meter Report'

    start_date = fields.Date(required=True, default=lambda self: date.today() )
    meter_data = fields.Many2many('sd_payaneh_nafti.meter_data', 'meter_data_report')

    # start_date = fields.Date(required=True, default=lambda self: date.today() )
    # calendar = fields.Selection([('fa_IR', 'Persian'), ('en_US', 'Gregorian')],
    #                             default=lambda self: 'fa_IR' if self.env.context.get('lang') == 'fa_IR' else 'en_US')

    # #############################################################################
    def process_report(self):
        read_form = self.read()[0]
        data = {'form_data': read_form}
        return self.env.ref('sd_payaneh_nafti.meter_report').report_action(self, data=data)

    @api.depends('start_date')
    @api.onchange('start_date')
    def _report_data_changed(self):
        if not self.start_date:
            return
        self.meter_data = False
        meters = {0, 1, 2, 3, 4, 5, 6, 7, 8, }
        this_date_model = self.env['sd_payaneh_nafti.meter_data']
        this_date_records = this_date_model.search([('report_date', '=', self.start_date)])
        this_meters = set([m.meter for m in this_date_records])
        needed_meters = meters.difference(this_meters)
        if needed_meters:
            for meter in needed_meters:
                this_date_model.create({'report_date': self.start_date, 'meter': meter})

        this_date_records = this_date_model.search([('report_date', '=', self.start_date)])
        print(f'{"* " * 30} \n this_meters: {this_meters} needed_meters: {needed_meters}\n {this_date_records}')
        self.meter_data = this_date_records.ids






































