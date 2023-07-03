# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
# import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
from colorama import Fore

class SdPayanehNaftiContractInfo(models.Model):
    _name = 'sd_payaneh_nafti.contract_registration'
    _description = 'sd_payaneh_nafti.contract_registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'registration_no'
    _rec_name = 'registration_no'

    registration_no = fields.Char(required=True,)
    contract_no = fields.Char(required=True,)
    bill_of_lading = fields.Char(required=True,)
    buyer = fields.Many2one('sd_payaneh_nafti.base_info',required=True,)
    amount = fields.Integer(required=True,)
    unit = fields.Selection([('barrel', 'Barrel'), ('metric_ton', 'Metric Ton')], default='metric_ton', required=True,)
    contract_type = fields.Selection([('stock', 'Stock'), ('general', 'General')], default='general', required=True,)
    loading_type = fields.Selection([('internal', 'Internal'), ('export', 'Export')], default='internal', required=True,)
    cargo_type = fields.Many2one('sd_payaneh_nafti.cargo_types',required=True,)
    start_date = fields.Date(default=lambda self: date.today() )
    end_date = fields.Date(default=lambda self: date.today() + timedelta(days=2) )
    destination = fields.Char(required=True,)
    shipment_1 = fields.Char()
    shipment_2 = fields.Char()
    shipment_3 = fields.Char()
    shipment_4 = fields.Char()
    shipment_5 = fields.Char()
    first_extend_no = fields.Char()
    first_extend_star_date = fields.Date(default=lambda self: date.today(), string='Start Date' )
    first_extend_end_date = fields.Date(default=lambda self: date.today() + timedelta(days=2), string='End Date')

    second_extend_no = fields.Char()
    second_extend_star_date = fields.Date(default=lambda self: date.today() , string='Start Date')
    second_extend_end_date = fields.Date(default=lambda self: date.today() + timedelta(days=2), string='End Date')


    description = fields.Char()

