# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
# import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from colorama import Fore

class SdPayanehNaftiBaseInof(models.Model):
    _name = 'sd_payaneh_nafti.base_info'
    _description = 'sd_payaneh_nafti.base_info'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'buyer'
    _rec_name = 'buyer'

    buyer = fields.Char(required=True,)
    contractor = fields.Char(required=True,)
    contract_no = fields.Char(required=True,)
    destination = fields.Char(required=True,)
    signers = fields.Char(required=True,)
    description = fields.Char()
