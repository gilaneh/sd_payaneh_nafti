# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
# import random
import jdatetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pytz
from colorama import Fore
import json

class SdPayanehNaftiLoadingPlan(models.Model):
    _name = 'sd_payaneh_nafti.loading_plan'
    _description = 'sd_payaneh_nafti.loading_plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    record_date = fields.Date(default=lambda self: datetime.now(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran'))), required=True,)
    registration_no = fields.Many2one('sd_payaneh_nafti.contract_registration')
    contract_unit = fields.Selection(related='registration_no.unit')
    contract_amount = fields.Integer(related='registration_no.amount')
    contract_remain_amount = fields.Integer(related='registration_no.remain_amount')
    remain_tankers = fields.Integer(compute="_remain_tankers")
    plan_1 = fields.Integer()
    plan_2 = fields.Integer()
    plan_3 = fields.Integer()
    plan_4 = fields.Integer()
    plan_5 = fields.Integer()
    plan_6 = fields.Integer()
    plan = fields.Integer(compute='_compute_plan')

    load_1 = fields.Integer(compute='_compute_load')
    load_2 = fields.Integer(compute='_compute_load')
    load_3 = fields.Integer(compute='_compute_load')
    load_4 = fields.Integer(compute='_compute_load')
    load_5 = fields.Integer(compute='_compute_load')
    load_6 = fields.Integer(compute='_compute_load')
    load = fields.Integer(compute='_compute_load')

    def _compute_load(self):
        the_day = list({rec.record_date for rec in self})[0]
        print(f'>>>>>>>>      load      {the_day}          ')
        loadings = self.env['sd_payaneh_nafti.input_info'].search([('request_date', '=', the_day )])

        for rec in self:
            rec.load_1 = len(list([r for r in loadings if r.registration_no == rec.registration_no and r.shift == 'shift_1']))
            rec.load_2 = len(list([r for r in loadings if r.registration_no == rec.registration_no and r.shift == 'shift_2']))
            rec.load_3 = len(list([r for r in loadings if r.registration_no == rec.registration_no and  r.shift == 'shift_3']))
            rec.load_4 = len(list([r for r in loadings if r.registration_no == rec.registration_no and  r.shift == 'shift_4']))
            rec.load_5 = len(list([r for r in loadings if r.registration_no == rec.registration_no and  r.shift == 'shift_5']))
            rec.load_6 = len(list([r for r in loadings if r.registration_no == rec.registration_no and  r.shift == 'shift_6']))
            rec.load = len(list([r for r in loadings if r.registration_no == rec.registration_no]))
    def _remain_tankers(self):
        for rec in self:
            if rec.contract_unit == 'barrel':
                rec.remain_tankers = round(rec.contract_remain_amount / 200)
            else:
                rec.remain_tankers = round(rec.contract_remain_amount / 22)

    def _compute_plan(self):
        for rec in self:
            rec.plan = rec.plan_1 + rec.plan_2 + rec.plan_3 + rec.plan_4 + rec.plan_5 + rec.plan_6

    def create_records(self):
        start_day = datetime.now(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran')))
        end_day = datetime.now(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran'))) + timedelta(days=3)
        for day in range(3):
            the_day = start_day + timedelta(days=day)
            contracts = self.env['sd_payaneh_nafti.contract_registration'].sudo().search([ '|', '|',
                                                                                          ('end_date', '>', the_day),
                                                                                          ('first_extend_end_date', '>', the_day),
                                                                                          ('second_extend_end_date', '>', the_day),

                                                                                          ])
            contracts = list([rec for rec in contracts if rec.remain_amount > 100])
            the_day_records = self.sudo().search([('record_date', '=', the_day)])
            the_day_records_reg_ids = list([rec.registration_no.id for rec in the_day_records])
            # print(f'/n LLLLL{the_day} {the_day_records_reg_ids}')
            lost_contracts = filter(lambda rec: rec.id not in the_day_records_reg_ids, contracts)

            for contract in lost_contracts:
                self.create({'record_date': the_day,
                             'registration_no': contract.id})

                # print(f'''
                #     contract: {contract}
                # ''')

    @api.model
    def loading_plans(self):
        self.create_records()
        lang = self.env.context.get('lang', 'en_US')
        start_day = datetime.now(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran'))).date()
        end_day = datetime.now(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran'))).date() + timedelta(days=3)
        plans = self.sudo().search([('record_date', '>=', start_day),
                                    ('record_date', '<=', end_day), ])
#         print(f'''
#             plans: {plans[0].registration_no.remain_amount}
#             plans: {plans[0].record_date}
# ''')

        plan_data = []
        for day in range(3):
            the_day = start_day + timedelta(days=day)
            remain_amount = list([rec.registration_no.remain_amount for rec in plans if rec.record_date == the_day])
            allocated = list([rec.plan for rec in plans if rec.record_date == the_day])

            print(f'/n the_day: {the_day}\n remain_amount: {remain_amount}\n allocated: {allocated}')
            plan_data.append({'index': day,
                              'date': the_day.strftime("%Y-%m-%d"),
                              's_date': self.convert_date(the_day, lang),
                              'remain_amount': round(sum(remain_amount) / 200),
                              'allocated': sum(allocated) ,
                              })
            # print(f'''
            #     contracts: day: {day} {the_day}
            # ''')
        plan_detail = []
        the_day_rec = list([rec for rec in plans if rec.record_date == start_day])

        data = {'data': plan_data, 'plan_detail': plan_detail}

        return json.dumps(data)

    def convert_date(self, date, lang):
        if lang == 'fa_IR':
            s_start_date = jdatetime.date.fromgregorian(date=date).strftime("%Y/%m/%d")
        else:
            s_start_date = date.strftime("%Y-%m-%d")
        return s_start_date


