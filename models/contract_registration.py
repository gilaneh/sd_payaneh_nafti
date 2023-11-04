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
    _order = 'registration_no desc'
    _rec_name = 'registration_no'

    registration_no = fields.Char(required=True, copy=False, readonly=True, default=lambda self: _('New'))
    letter_no = fields.Char(required=True,)
    contract_no = fields.Char(required=True,)
    bill_of_lading = fields.Char(required=False,)
    order_no = fields.Char(required=False,)
    buyer = fields.Many2one('sd_payaneh_nafti.buyers', required=True,)
    amount = fields.Integer(required=True,)
    unit = fields.Selection([('barrel', 'Barrel'), ('metric_ton', 'Metric Ton')], default='metric_ton', required=True,)
    contract_type = fields.Selection([('stock', 'Stock'), ('general', 'General')], default='general', required=True,)
    loading_type = fields.Selection([('internal', 'Internal'), ('export', 'Export')], default='internal', required=True,)
    cargo_type = fields.Many2one('sd_payaneh_nafti.cargo_types',required=True,)
    start_date = fields.Date(default=lambda self: date.today() )
    end_date = fields.Date(default=lambda self: date.today() + timedelta(days=2) )
    destination = fields.Many2one('sd_payaneh_nafti.destinations', required=True,)
    contractors = fields.Many2many('sd_payaneh_nafti.contractors', 'registration_contractors_rel', required=False,)

    first_extend_no = fields.Char()
    first_extend_star_date = fields.Date(string='First Start Date')
    first_extend_end_date = fields.Date(string='First End Date')

    second_extend_no = fields.Char()
    second_extend_star_date = fields.Date( string='Second Start Date')
    second_extend_end_date = fields.Date( string='Second End Date')


    description = fields.Char()

    def copy_order_no(self):
        for rec in self:
            rec.order_no = rec.bill_of_lading
    @api.model
    def create(self, vals):
        if vals.get('registration_no', _('New')) == _('New'):
            vals['registration_no'] = self.env['ir.sequence'].next_by_code('sd_payaneh_nafti.contract_registration') or _('New')

        return super(SdPayanehNaftiContractInfo, self).create(vals)

class SdPayanehNaftiContractInfoInit(models.Model):
    _inherit = 'sd_payaneh_nafti.contract_registration'

    init_date = fields.Date()
    init_amount = fields.Integer()