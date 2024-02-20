# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
import json

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
from colorama import Fore
import jdatetime
import math
import logging
import pytz


cpl_counter = 0
def _cpl_counter():
    global cpl_counter
    cpl_counter += 1
    return cpl_counter
class SdPayanehNaftiInputInfo(models.Model):
    _name = 'sd_payaneh_nafti.input_info'
    _description = 'sd_payaneh_nafti.input_info'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'document_no desc'
    _rec_name = 'document_no'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('loading_permit', 'Loading Permit'),
        ('loading_info', 'Loading Info'),
        ('cargo_document', 'Cargo Doc'),
        ('done', 'Done'),
        ('driver_block_list', 'Driver'),
        ('truck_black_list', 'Truck'),
        ('out_of_date', 'Out of Date'),
        ('amount_limit', 'Amount Limit'),
        ('finished', 'Finished'),
        ],
        string='Status', index=True, readonly=True, tracking=True,
        copy=False, default='draft', required=True, group_expand='_expand_groups', )
    remain_amount = fields.Float(compute='_remain_amount')
    remain_amount_approx = fields.Float(compute='_remain_amount')
    amount = fields.Float()
    document_no = fields.Integer(required=True, copy=False, readonly=False, default=lambda self: 0)
    request_date = fields.Date(default=lambda self: datetime.now(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran'))), required=True,)
    registration_no = fields.Many2one('sd_payaneh_nafti.contract_registration', required=True,
                                      default=lambda self: self.env.context.get('registration_no', False))
    date_validation = fields.Boolean(related='registration_no.date_validation', store=False)
    contract_no = fields.Char(related='registration_no.contract_no',)
    order_no = fields.Char(related='registration_no.order_no')
    buyer = fields.Many2one(related='registration_no.buyer')
    contractors = fields.Many2many(related='registration_no.contractors')
    contractor = fields.Many2one('sd_payaneh_nafti.contractors', required=True,)
    driver = fields.Many2one('sd_payaneh_nafti.drivers', required=True,)
    driver_black_list = fields.Boolean(related='driver.black_list')
    card_no = fields.Char(related='driver.card_no')
    truck_no = fields.Many2one('sd_payaneh_nafti.trucks', required=True,)
    truck_black_list = fields.Boolean(related='truck_no.black_list')
    plate_1 = fields.Char(related='truck_no.plate_1',)
    plate_2 = fields.Char(related='truck_no.plate_2',)
    plate_3 = fields.Char(related='truck_no.plate_3',)
    plate_4 = fields.Char(related='truck_no.plate_4',)
    front_container = fields.Integer(required=True,)
    middle_container = fields.Integer(required=True,)
    back_container = fields.Integer(required=True,)
    total = fields.Integer(compute='_total')
    centralized_container = fields.Selection([('a', 'A'),
                                              ('b', 'B'),
                                              ('c', 'C'),
                                              ('d', 'D'),
                                              ('e', 'E'),
                                              ('f', 'F'),
                                              ('g', 'G'),
                                              ('h', 'H'),
                                              ], required=True,)

    loading_no = fields.Char(copy=False, readonly=True, )
    # todo: timezone
    loading_date = fields.Date(copy=False, readonly=False, default=lambda self: self.request_date)
    loading_info_date = fields.Date(copy=False, default=lambda self: datetime.now(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran'))))
    # driver = fields.Char(required=True,)

    sp_gr = fields.Float( string='SP. GR.', required=True, default=0.7252, store=True, readonly=True)
    # sp_gr = fields.Many2one('sd_payaneh_nafti.spgr', string='SP. GR.', required=True, default=0.7252)
    temperature = fields.Integer(string='Temp. (C)', required=True, default=30)
    temperature_f = fields.Float(string='Temp. (F)', compute='_temperature_f', digits=(12, 1))
    pressure = fields.Float(string='Pressure (bar)', required=True, default=2.5)
    pressure_psi = fields.Integer(compute='_pressure_psi')
    meter_no = fields.Selection([ ('1', '1'),
                                  ('2', '2'),
                                  ('3', '3'),
                                  ('4', '4'),
                                  ('5', '5'),
                                  ('6', '6'),
                                  ('7', '7'),
                                  ('8', '8'),
                                  ('0', 'Master'),
                                  ], required=False,)
    totalizer_start = fields.Integer(required=False,)
    totalizer_end = fields.Integer(required=False,)
    totalizer_difference = fields.Integer(required=False, compute='_totalizer_difference')
    weighbridge = fields.Selection([('no', 'No'), ('yes', 'Yes')], default='no')
    tanker_empty_weight = fields.Integer(required=False,)
    tanker_full_weight = fields.Integer(required=False,)
    tanker_pure_weight = fields.Integer(required=False, compute='_tanker_pure_weight')
    evacuation_box_seal = fields.Char(required=False,)
    compartment_1 = fields.Char(required=False,)
    compartment_2 = fields.Char(required=False,)
    compartment_3 = fields.Char(required=False,)
    correction_factor = fields.Float(digits=(12, 5), required=True, default=1.0)
    # api_box_locker = fields.Many2one('sd_payaneh_nafti.lockers')
    # compartment_locker_1 = fields.Many2one('sd_payaneh_nafti.lockers')
    # compartment_locker_2 = fields.Many2one('sd_payaneh_nafti.lockers')
    # compartment_locker_3 = fields.Many2one('sd_payaneh_nafti.lockers')

    api_a = fields.Float(string='API', compute='_api_a')
    ctl = fields.Float(string='CTL', compute='_ctl_cpl')
    cpl = fields.Float(string='CPL', compute='_ctl_cpl')
    tab_13 = fields.Float(string='TAB.13', digits=(12, 5), compute='_tab_13')
    # this variables are useless
    meter_tov_l = fields.Float(string='Meter T.O.V Liter')
    meter_gsv_l = fields.Float(string='Meter G.S.V Liter')
    meter_gsv_b = fields.Float(string='Meter G.S.V BBL', digits=[8, 2])
    meter_mt = fields.Float(string='Meter M.T.')
    wb_tov_l = fields.Float(string='WB T.O.V Liter')
    wb_gsv_l = fields.Float(string='WB G.S.V Liter')
    wb_gsv_b = fields.Float(string='WB G.S.V BBL', digits=[8, 2])
    wb_mt = fields.Float(string='WB M.T.')

    final_tov_l = fields.Float(string='Final T.O.V Liter', compute='_finals', digits=[8, 0])
    final_gsv_l = fields.Float(string='Final G.S.V Liter', compute='_finals', digits=[8, 0])
    final_gsv_b = fields.Float(string='Final G.S.V BBL', compute='_finals', )
    final_mt = fields.Float(string='Final M.T.', compute='_finals', digits=[8, 3])
    cpl_counter = fields.Integer(default=0)

    # def drivers_strip(self):
    #     ids = self.env.context.get('active_ids')
    #     print(f'\n active ids: {ids}')
        # for rec in self:
        #     rec.driver = rec.driver.strip()

    # def drivers_create(self):
    #     ids = self.env.context.get('active_ids')
    #     print(f'\n active ids: {ids}')
    #     records = self.browse(ids)
    #     drivers_model = self.env['sd_payaneh_nafti.drivers']
        # for rec in records:
        #     if not drivers_model.search([('name', '=', rec.driver)]):
        #         drivers_model.create({'name': rec.driver})
        #     drivers = drivers_model.search([('name', '=', rec.driver)])
        #     if len(drivers) == 1:
        #         rec.write({'driver_name': drivers.id})

    @api.onchange('document_no')
    def onchange_document_no(self):
        self.set_spgr()

    @api.depends('registration_no',)
    @api.onchange('registration_no', 'front_container', 'middle_container', 'back_container')
    def _on_registration_change(self):
        self._remain_amount()

    @api.onchange('weighbridge')
    def _onchange_weighbridge(self):
        self._finals()
        self._weighbridge_change()

    @api.onchange('temperature')
    def _onchange_temperature(self):
        self._temperature_f()
        self._ctl_cpl()

    @api.onchange('sp_gr')
    def _onchange_spgr(self):
        self._api_a()
        self._tab_13()
        self._ctl_cpl()

    @api.onchange('pressure')
    def _onchange_pressure(self):
        self._pressure_psi()
        self._ctl_cpl()

    def set_spgr(self):
        # if not self.env.user.has_group('sd_payaneh_nafti.group_sd_payaneh_nafti_operators'):
        #     return
        spgr = self.env['sd_payaneh_nafti.spgr'].search([], order='id desc', limit=1)
        if len(spgr) == 1:
            self.sp_gr = spgr.spgr
        else:
            raise ValidationError(_('Add a "SP.GR." from the main menu'))

    def _remain_amount(self):
        for rec in self:
            final_gsv_b = 0
            final_mt = 0
            requested_approx_amount = 0

            # todo: this algorithm might be too slow. I calculate's the remain amount each time for each of the records.
            #   It can be done for each of them and be stored on the record.

            # In case of new record creation
            if rec.id and str(rec.id).isdigit():
                inputs = self.search([('id', '!=', False), ('id', '<=', rec.id), ('registration_no', '=', rec.registration_no.id), ])
            else:
                inputs = self.search([('registration_no', '=', rec.registration_no.id),])

            #  if there is no loading info, calculate based on sum of the containers amount
            if not rec.final_mt:
                total = rec.front_container + rec.middle_container + rec.back_container
                # final_tov_l = round((rec.cpl * total * rec.correction_factor), 0 )
                final_gsv_l = round((rec.cpl * rec.ctl * total * rec.correction_factor), 0 )
                final_gsv_b = final_gsv_l / 158.987
                final_mt = round(final_gsv_b * rec.tab_13, 3)

            # calculate the used amounts basd on contract unit type; barrel or metric/tone
            if rec.registration_no.unit == 'barrel':
                used_amounts = sum([ua.final_gsv_b for ua in inputs])
                requested_approx_amount = final_gsv_b
            elif rec.registration_no.unit == 'metric_ton':
                used_amounts = sum([ua.final_mt for ua in inputs])
                requested_approx_amount = final_mt

            else:
                used_amounts = 0


            amount = rec.registration_no.amount if rec.registration_no.init_amount == 0 else rec.registration_no.init_amount
            rec.remain_amount = amount - used_amounts
            rec.remain_amount_approx = amount - used_amounts - requested_approx_amount
            if rec.state != 'finished':
                rec.amount = rec.final_gsv_b if rec.registration_no.unit == 'barrel' else rec.final_mt

            # if rec.remain_amount_approx < 0:
            #     raise ValidationError(_(f'Document No: {rec.document_no}'
            #                             f'\nRegistration No: {rec.registration_no}'
            #                             f'\nContract amount: {amount}'
            #                             f'\nRemain amount: {rec.remain_amount}'
            #                             f'\nRequested amount: {requested_approx_amount}'
            #                             f'\nApproximate remain amount: {rec.remain_amount_approx}'))

    def _finals(self):
        # calculate the final amounts based on the totalizer or the tanker weight
        for rec in self:
            if rec.weighbridge == 'yes':
                final_mt = round(rec.tanker_pure_weight / 1000, 3)
                final_gsv_b = final_mt / rec.tab_13
                final_gsv_l = round(final_gsv_b * 158.987, 0)
                final_tov_l = round((final_gsv_l / rec.ctl) / rec.cpl, 0)
            else:
                final_tov_l = round((rec.cpl * rec.totalizer_difference * rec.correction_factor), 0 )
                final_gsv_l = round((rec.cpl * rec.ctl * rec.totalizer_difference * rec.correction_factor), 0 )
                final_gsv_b = final_gsv_l / 158.987
                final_mt = round(final_gsv_b * rec.tab_13, 3)

            rec.final_mt = final_mt
            rec.final_gsv_b = final_gsv_b
            rec.final_gsv_l = final_gsv_l
            rec.final_tov_l = final_tov_l

    def _temperature_f(self):
        # calculates the temperature based on Fahrenheit degree
        for rec in self:
            rec.temperature_f = rec.temperature * 9 / 5 + 32

    def _api_a(self):
        # calculates the API
        for rec in self:
            api_a = 141.5 / rec.sp_gr - 131.5 if rec.sp_gr else 0
            rec.api_a = round(api_a, 2) if rec.registration_no.loading_type == 'internal' else round(api_a, 1)

    def _tab_13(self):
        # Calculates the TAB.13
        for rec in self:
            rec.tab_13 = ((141.3819577 / (rec.api_a + 131.5)) - 0.001199407795) * 0.1589872949


    def _pressure_psi(self):
        # Calculates the pressure based on PSI
        for rec in self:
            rec.pressure_psi = rec.pressure * 14.5038

    def _ctl_cpl(self):
        # takes the constant parameters from setting page
        k_0 = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.k_0'))
        k_1 = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.k_1'))
        k_2 = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.k_2'))
        delta_60 = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.delta_60'))
        tref = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.tref'))
        param_a = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.param_a'))
        param_b = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.param_b'))
        param_c = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.param_c'))
        param_d = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.param_d'))
        param_ai1 = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.param_ai1'))
        param_ai2 = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.param_ai2'))
        param_ai3 = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.param_ai3'))
        param_ai4 = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.param_ai4'))
        param_ai5 = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.param_ai5'))
        param_ai6 = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.param_ai6'))
        param_ai7 = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.param_ai7'))
        param_ai8 = float(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.param_ai8'))

        # logging.error(f'%%%%%%%%%%%% > cpl_counter: {_cpl_counter()} k_0: {k_0} delta_60: {delta_60} ')
        # Calculates CPL and CTL which they will be used to calculate the other parameters
        for rec in self:
            try:
                rec_pi = (141.5 / (rec.api_a + 131.5)) * 999.016
                rec_a = (delta_60 / 2) * (((k_0 / rec_pi) + k_1) * (1 / rec_pi) + k_2)
                rec_b = ((2 * k_0) + (k_1 * rec_pi)) / ((k_0 + ((k_2 * rec_pi) + k_1) * rec_pi))
                rec_pi_star = rec_pi * (1 + ((math.exp((rec_a * (1 + (0.8 * rec_a)))) - 1) / (1 + rec_a * (1 + (0.6 * rec_a)) * rec_b)))
                alpha_60 = (((k_0 / rec_pi_star) + k_1) * (1 / rec_pi_star)) + k_2
                t_star_prime = ((rec.temperature_f-32)/1.8)/630
                t_star_zegond = (param_ai1+((param_ai2+((param_ai3+((param_ai4+((param_ai5+((param_ai6+((param_ai7+(param_ai8*t_star_prime))*t_star_prime))*t_star_prime))*t_star_prime))*t_star_prime))*t_star_prime))*t_star_prime))*t_star_prime
                t_star = ((rec.temperature-((param_ai1+(param_ai2+(param_ai3+(param_ai4+(param_ai5+(param_ai6+(param_ai7+param_ai8*(rec.temperature/630))*(rec.temperature/630))*(rec.temperature/630))*(rec.temperature/630))*(rec.temperature/630))*(rec.temperature/630))*(rec.temperature/630))*(rec.temperature/630)))*1.8)+32
                delta_t = t_star - tref
                fp = math.exp((param_a+param_b*t_star+((param_c+param_d*t_star)/(rec_pi_star**2))))
                rec.ctl = math.exp((-(alpha_60 * delta_t)) * (1 + ((0.8 * alpha_60) * (delta_t + delta_60))))
                rec.cpl = 1 / (1-((10 ** -5) * (fp * rec.pressure_psi)))
                # print(f'\nrec_pi: {rec_pi}\nrec_a: {rec_a}\nrec_b: {rec_b}\nrec_pi_star: {rec_pi_star}\nalpha_60: {alpha_60}\n  ')
            except Exception as e:
                logging.error(f'_ctl_cpl : {e}')
                logging.error(f'_ctl_cpl : You might needed to save system parameters')
                rec.ctl = 1
                rec.cpl = 1
                raise ValidationError(_('You might needed to save system parameters.'
                                        '\n They get default values but you have to save them to res.config.system.'))

    def _weighbridge_change(self):
        # It makes sure the tanker weight or the totalizer amount would be zero whenever the weighbridge has changed.
        for rec in self:
            if rec.weighbridge == 'no':
                rec.write({'tanker_empty_weight': 0, 'tanker_full_weight': 0, })

    @api.onchange('front_container', 'middle_container', 'back_container')
    def _total(self):
        # It calculates the total amount of tanker containers
        for rec in self:
            rec.total = rec.front_container + rec.middle_container + rec.back_container

    @api.onchange('totalizer_end', 'totalizer_start')
    def _totalizer_difference(self):
        # It calculates the totalizer difference based on totalizer start amount and its end amount
        for rec in self:
            rec.totalizer_difference = rec.totalizer_end - rec.totalizer_start

    @api.onchange('tanker_full_weight', 'tanker_empty_weight')
    def _tanker_pure_weight(self):
        # It calculates the loaded amount based on calculation of tanker full weight and its empty weight.
        for rec in self:
            rec.tanker_pure_weight = rec.tanker_full_weight - rec.tanker_empty_weight

    @api.constrains('document_no')
    def _check_document_no_unique(self):
        # It makes sure the document number is unique
        record_count = self.search_count([('document_no', '=', self.document_no), ('id', '!=', self.id)])
        if record_count > 0:
            raise ValidationError("Record already exists!")

    @api.model
    def create(self, vals):


        # todo: it is disabled for parallel data entry of excel and this system.
        # if vals.get('document_no', 0) == 0:
        #     vals['document_no'] = self.env['ir.sequence'].next_by_code('sd_payaneh_nafti.input_info') or 0

            # todo: timezone, last ours of 29'th of Esfand might show a wrong date, maybe first of next year
            # vals['loading_no'] = str(jdatetime.date.today().year) + f"/{int(vals['document_no']):07d}"



        spgr = self.env['sd_payaneh_nafti.spgr'].search([], order='id desc', limit=1)
        if len(spgr) == 1:
            vals['sp_gr'] = spgr.spgr
        else:
            raise ValidationError(_('Add a "SP.GR." from the main menu'))
        if vals.get('meter_no') and type(vals.get('meter_no')) == str and vals.get('meter_no').lower() == 'master':
            vals['meter_no'] = '0'
        return super(SdPayanehNaftiInputInfo, self).create(vals)

    def write(self, vals):
        # Changing the compartment_1 means that there are loading info entry. So, it moves the state to cargo_document.
        if vals.get('compartment_1') or vals.get('compartment_locker_1'):
            vals['state'] = 'cargo_document'
        if not self.env.is_admin() and self.state == 'finished':
#             print(f'''
#                 vals: {vals}
# ''')
            raise ValidationError(_('Finished record is not editable!'))

        return super(SdPayanehNaftiInputInfo, self).write(vals)

    def get_contract_registration(self):
        # On the input_info form, there is a button named "Contract" which it shows the related contract of this input
        #   info.
        self.ensure_one()
        form_id = self.env.ref('sd_payaneh_nafti.sd_payaneh_nafti_contract_registration_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inputs',
            'views': [ [form_id, 'form']],
            'view_mode': 'form',
            'res_id': self.registration_no.id,
            'res_model': 'sd_payaneh_nafti.contract_registration',
            'context': "{'create': False}"
        }

    def loading_permit(self):
        # In input info for, there is a button named "Loading Permit" which updates some fields.
        for rec in self:
            loading_no = str(jdatetime.date.today().year) + f"/{int(rec.document_no):07d}"
            loading_date = datetime.now(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran'))).date()
            rec.write({'state': 'loading_permit', 'loading_no': loading_no, 'loading_date': loading_date })

    def print_loading_permit(self):

        if self.state == 'loading_permit':
            self.write({'state': 'loading_info'})
        data = {'form_data': {'document_no': (0, self.document_no)}}
        return self.env.ref('sd_payaneh_nafti.loading_permit_report').report_action(self, data=data)

    def loading_info(self):
        data = {'form_data': {'document_no': (0, self.document_no)}}
        loading_info_form = self.env.ref('sd_payaneh_nafti.sd_payaneh_nafti_input_info_form_loading_info')
        # print(f'\n loading info: self: {self} loading_info_form: {loading_info_form}')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Loading Info',
            'views': [[loading_info_form.id, 'form']],
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'res_model': 'sd_payaneh_nafti.input_info',
            # 'context': "{'create': False}"
        }

    def print_cargo_document(self):
        data = {'form_data': {'document_no': (0, self.document_no), 'calendar': 'fa_IR'}}
        return self.env.ref('sd_payaneh_nafti.cargo_document_report').report_action(self, data=data)

    def input_done(self):
        for rec in self:
            rec.write({'state': 'done'})


    def input_finished(self):
        for rec in self:
            rec.write({'state': 'finished'})

    @api.model
    def get_requests(self):
        today_date = date.today()
        print(f'------------> today_date: {today_date}')

        open_requests = self.search([('state', 'not in', ['done', 'finished'])])
        this_day_requests = self.search([('request_date', '=', today_date)])

        # todo: amount is not comparable between contracts with different unit type.
        #   amount for barrel is calculated based on final_bbl
        #   amount for metric tone is calculated based on final_mt
        #   so the remain amount of this two type of contracts should not be sum up.
        this_day_loaded = self.search([('loading_info_date', '=', today_date)])
        this_day_requests_amount = round(sum([rec.amount for rec in this_day_loaded ]), 2)
        this_day_requests_amount = 0

        this_day_requests_count = len(this_day_requests)
        new_requests = len([rec for rec in open_requests if rec.state == 'draft'])
        loading_permit = len([rec for rec in open_requests if rec.state == 'loading_permit'])
        loading_info = len([rec for rec in open_requests if rec.state == 'loading_info'])


        cargo_document = len([rec for rec in open_requests if rec.state == 'cargo_document'])


        data = {
            'open_requests': len(open_requests),
            'this_day_requests_count': this_day_requests_count,
            'this_day_requests_amount': this_day_requests_amount,
            'new_requests': new_requests,
            'loading_permit': loading_permit,
            'loading_info': loading_info,
            'cargo_document': cargo_document,
        }
        return json.dumps(data)



class SdPayanehNaftiPlate1(models.Model):
    _name = 'sd_payaneh_nafti.plate1'
    _description = 'sd_payaneh_nafti.plate1'

    name = fields.Char(translate=True)


class SdPayanehNaftiPlate2(models.Model):
    _name = 'sd_payaneh_nafti.plate2'
    _description = 'sd_payaneh_nafti.plate2'

    name = fields.Char(translate=True)


class SdPayanehNaftiPlate3(models.Model):
    _name = 'sd_payaneh_nafti.plate3'
    _description = 'sd_payaneh_nafti.plate3'

    name = fields.Char(translate=True)

class SdPayanehNaftiPlate4(models.Model):
    _name = 'sd_payaneh_nafti.plate4'
    _description = 'sd_payaneh_nafti.plate4'

    name = fields.Char(translate=True)


