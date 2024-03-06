# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
# import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from colorama import Fore

class SdPayanehNaftContractDailyQuantity(models.Model):
    _name = 'sd_payaneh_nafti.buyers'
    _description = 'sd_payaneh_nafti.contract_daily_quantity'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    record_date = fields.Date(default=lambda self: datetime.now(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran'))), required=True,)
    registration_no = fields.Many2one('sd_payaneh_nafti.contract_registration')


