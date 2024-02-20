# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
import json

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

    registration_no = fields.Char(required=True, copy=False, readonly=False, default=lambda self: _('New'))
    letter_no = fields.Char(required=True,)
    contract_no = fields.Char(required=True,)
    bill_of_lading = fields.Char(required=False,)
    order_no = fields.Char(required=False,)
    buyer = fields.Many2one('sd_payaneh_nafti.buyers', required=True,)
    amount = fields.Integer(required=True,)
    unit = fields.Selection([('barrel', _('Barrel')), ('metric_ton', _('Metric Ton'))], default='barrel', required=True, translate=True)
    contract_type = fields.Selection([('stock', _('Stock')), ('general', _('General'))], default='general', required=True)
    loading_type = fields.Selection([('internal', _('Internal')), ('export', _('Export'))], default='internal', required=True)
    cargo_type = fields.Many2one('sd_payaneh_nafti.cargo_types', required=True, default=lambda self: self.env['sd_payaneh_nafti.cargo_types'].search([], limit=1,).id)
    start_date = fields.Date(default=lambda self: date.today(), required=True)
    end_date = fields.Date(default=lambda self: date.today() + timedelta(days=20), required=True)
    destination = fields.Many2one('sd_payaneh_nafti.destinations', required=True)
    contractors = fields.Many2many('sd_payaneh_nafti.contractors', 'registration_contractors_rel', required=True)

    first_extend_no = fields.Char()
    first_extend_star_date = fields.Date(string='First Start Date')
    first_extend_end_date = fields.Date(string='First End Date')

    second_extend_no = fields.Char()
    second_extend_star_date = fields.Date(string='Second Start Date')
    second_extend_end_date = fields.Date(string='Second End Date')
    input_count = fields.Integer(compute='compute_count')
    remain_amount = fields.Integer(compute='compute_remain_amount')
    date_validation = fields.Boolean(default=True, compute='_date_validation')
    description = fields.Char()

    @api.depends('registration_no')
    def _date_validation(self):
        for rec in self:
            today = date.today()
            if rec.end_date and rec.end_date > today \
                    or rec.first_extend_end_date and rec.first_extend_end_date > today \
                    or rec.second_extend_end_date and rec.second_extend_end_date > today:
                rec.date_validation = True
            else:
                rec.date_validation = False
            # print(f'\n---------->   registration_no: {rec.registration_no} date_validation: {rec.date_validation} ')

    def compute_count(self):
        for rec in self:
            rec.input_count = self.env['sd_payaneh_nafti.input_info'].search_count(
                [('registration_no', '=', rec.registration_no)])

    def compute_remain_amount(self):
        for rec in self:
            inputs = self.env['sd_payaneh_nafti.input_info'].search([('registration_no', '=', rec.id)])
            amounts_barrel = [rec.final_gsv_b for rec in inputs if rec.registration_no.unit == 'barrel']
            amounts_metric_ton = [rec.final_mt for rec in inputs if rec.registration_no.unit == 'metric_ton']
            amount = rec.amount if rec.init_amount == 0 else rec.init_amount
            rec.remain_amount = amount - sum(amounts_barrel) - sum(amounts_metric_ton)
    def copy_order_no(self):
        for rec in self:
            rec.order_no = rec.bill_of_lading
    @api.model
    def create(self, vals):
        # todo: it is disabled for parallel data entry of excel and this system.

        # if vals.get('registration_no', _('New')) == _('New'):
        #     vals['registration_no'] = self.env['ir.sequence'].next_by_code('sd_payaneh_nafti.contract_registration') or _('New')

        return super(SdPayanehNaftiContractInfo, self).create(vals)

    def get_inputs(self):
        self.ensure_one()
        form_id = self.env.ref('sd_payaneh_nafti.sd_payaneh_nafti_input_info_form_1').id
        list_id = self.env.ref('sd_payaneh_nafti.sd_payaneh_nafti_input_info_list_1').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inputs',
            'views': [[list_id, 'list'], [form_id, 'form']],
            'view_mode': 'tree,form',
            'res_model': 'sd_payaneh_nafti.input_info',
            'domain': [('registration_no', '=', self.registration_no)],
            'context': {'search_default_registration_no_group': 1}
        }


    def get_remain_amount(self):
        self.ensure_one()

    def create_loading_request(self):
        self.ensure_one()
        form_id = self.env.ref('sd_payaneh_nafti.sd_payaneh_nafti_input_info_form_1').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inputs',
            'views': [[form_id, 'form']],
            'view_mode': 'form',
            'res_model': 'sd_payaneh_nafti.input_info',
            'target': 'new',
            # 'domain': [('registration_no', '=', self.registration_no)],
            'context': {'registration_no': self.id}
        }

    @api.model
    def get_contracts(self):
        today_date = date.today()
        open_contracts = self.search(['|', '|', ('end_date', '>', today_date),
                                        ('first_extend_end_date', '>', today_date),
                                        ('second_extend_end_date', '>', today_date),
                                        ('remain_amount', '>', 0),
                                        ])

        # todo: amount is not comparable between contracts with different unit type.
        #   amount for barrel is calculated based on final_bbl
        #   amount for metric tone is calculated based on final_mt
        #   so the remain amount of this two type of contracts should not be sum up.
        remain_amount = round(sum([rec.remain_amount for rec in open_contracts]), 2)
        remain_amount = 0

        data = {
            'open_contracts': len(open_contracts),
            'remain_amount': f'{remain_amount:,}',
        }
        return json.dumps(data)

class SdPayanehNaftiContractInfoInit(models.Model):
    _inherit = 'sd_payaneh_nafti.contract_registration'

    init_date = fields.Date()
    init_amount = fields.Integer()