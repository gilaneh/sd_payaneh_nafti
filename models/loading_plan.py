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
    shift_1 = fields.Integer()
    shift_2 = fields.Integer()
    shift_3 = fields.Integer()
    shift_4 = fields.Integer()
    shift_5 = fields.Integer()
    shift_6 = fields.Integer()
    total = fields.Integer(compute='_compute_total')

    def _remain_tankers(self):
        for rec in self:
            if rec.contract_unit == 'barrel':
                rec.remain_tankers = round(rec.contract_remain_amount / 200)
            else:
                rec.remain_tankers = round(rec.contract_remain_amount / 22)

    def _compute_total(self):
        for rec in self:
            rec.total = rec.shift_1 + rec.shift_2 + rec.shift_3 + rec.shift_4 + rec.shift_5 + rec.shift_6

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
        print(f'''
            plans: {plans[0].registration_no.remain_amount}
            plans: {plans[0].record_date}
''')

        plan_data = []
        for day in range(3):
            the_day = start_day + timedelta(days=day)
            remain_amount = list([rec.registration_no.remain_amount for rec in plans if rec.record_date == the_day])
            allocated = list([rec.total for rec in plans if rec.record_date == the_day])

            print(f'/n the_day: {the_day}\n remain_amount: {remain_amount}\n allocated: {allocated}')
            plan_data.append({'index': day,
                              'date': self.convert_date(the_day, lang),
                              'remain_amount': round(sum(remain_amount) / 200),
                              'allocated': sum(allocated) ,
                              })
            # print(f'''
            #     contracts: day: {day} {the_day}
            # ''')
        data = {'data': plan_data}

        return json.dumps(data)

    def convert_date(self, date, lang):
        if lang == 'fa_IR':
            s_start_date = jdatetime.date.fromgregorian(date=date).strftime("%Y/%m/%d")
        else:
            s_start_date = date.strftime("%Y-%m-%d")
        return s_start_date
