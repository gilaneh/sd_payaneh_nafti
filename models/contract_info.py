# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
# import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
from colorama import Fore

class SdPayanehNaftiContractInfo(models.Model):
    _name = 'sd_payaneh_nafti.contract_info'
    _description = 'sd_payaneh_nafti.contract_info'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'registration_no'
    _rec_name = 'registration_no'

    registration_no = fields.Char(required=True,)
    contract_no = fields.Char(required=True,)
    bill_of_lading = fields.Char(required=True,)
    buyer = fields.Many2one('sd_payaneh_nafti.base_info',required=True,)
    destination = fields.Char(required=True,)
    start_date = fields.Date(default=lambda self: date.today() )
    end_date = fields.Date(default=lambda self: date.today() + timedelta(days=2) )

    delivering_amount = fields.Integer(required=True,)
    unit = fields.Selection([('barrel', 'Barrel'), ('metric_ton', 'Metric Ton')],
                            default='metric_ton', required=True,
                            help=_('159 litres (42 US gallon) of oil. There are about 7.1 barrels in one metric ton of oil.') )
    delivered_amount = fields.Integer(required=True,)
    remaining_amount = fields.Integer(required=True,)



    description = fields.Char()

