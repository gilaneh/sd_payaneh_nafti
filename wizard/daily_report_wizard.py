# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo import Command
from colorama import Fore
from datetime import datetime, date
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError

# #############################################################################
class SdPayanehNaftiReportDaily(models.TransientModel):
    _name = 'sd_payaneh_nafti.report.daily_report'
    _description = 'Daily Report'



    start_date = fields.Date(required=True, default=lambda self: date.today() )
    calendar = fields.Selection([('fa_IR', 'Persian'), ('en_US', 'Gregorian')],
                                default=lambda self: 'fa_IR' if self.env.context.get('lang') == 'fa_IR' else 'en_US')

    # #############################################################################
    def daily_report(self):
        read_form = self.read()[0]
        data = {'form_data': read_form}

        return self.env.ref('sd_payaneh_nafti.daily_report').report_action(self, data=data)


