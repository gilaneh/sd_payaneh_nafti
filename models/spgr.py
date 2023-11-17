# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
# import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from colorama import Fore

class SdPayanehNaftiSpgr(models.Model):
    _name = 'sd_payaneh_nafti.spgr'
    _description = 'sd_payaneh_nafti.spgr'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'spgr'

    active = fields.Boolean(default=True)
    spgr = fields.Float(required=True, digits=[1, 4])
    spgr_date = fields.Date(required=True, default=lambda self: fields.Date.today() )
    description = fields.Char()

    @api.model
    def create(self, vals):
        if vals.get('spgr', 0) > 1.1:
            raise ValidationError(_(f'{vals.get("spgr")} is not accepted!'))
        active_records = self.search([('active', '=', True)])
        for rec in active_records:
            rec.active = False
        return super(SdPayanehNaftiSpgr, self).create(vals)

    @api.onchange('spgr')
    def change_spgr(self):
        if self.spgr > 1.1:
            raise ValidationError(_(f'{self.spgr} is not accepted!'))

