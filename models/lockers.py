# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
# import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from colorama import Fore

class SdPayanehNaftiLockers(models.Model):
    _name = 'sd_payaneh_nafti.lockers'
    _description = 'sd_payaneh_nafti.lockers'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(required=True,)
    input_info = fields.Integer()
    input_info_type = fields.Char()
    description = fields.Char()

class SdPayanehNaftiLockersInputInfo(models.Model):
    _inherit = 'sd_payaneh_nafti.input_info'

    api_box_locker = fields.Many2one('sd_payaneh_nafti.lockers', )
    compartment_locker_1 = fields.Many2one('sd_payaneh_nafti.lockers', )
    compartment_locker_2 = fields.Many2one('sd_payaneh_nafti.lockers', )
    compartment_locker_3 = fields.Many2one('sd_payaneh_nafti.lockers', )
    # compartment_locker_1 = fields.One2many('sd_payaneh_nafti.lockers', 'input_info', 'locer_1_input')
    # compartment_locker_2 = fields.One2many('sd_payaneh_nafti.lockers', 'input_info', 'locer_2_input' )
    # compartment_locker_3 = fields.One2many('sd_payaneh_nafti.lockers', 'input_info', 'locer_3_input' )

    @api.onchange('api_box_locker')
    def change_api_box_locker(self):
        # print(f'\n {self.api_box_locker}')
        pass

    def write(self, vals):
        # vlas.get('rec', 0) =>
        #       0 : No change
        #   False : removed
        # Integer : changed
        # print(f'\n write {vals}, {self.api_box_locker}')
        if vals.get('api_box_locker'):
            pass
            # print(f'\n api_box_locker: {vals.get("api_box_locker")}')
        return super(SdPayanehNaftiLockersInputInfo, self).write(vals)
