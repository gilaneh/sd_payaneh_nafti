# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
# import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
from colorama import Fore
import jdatetime
import math
import logging

class SdPayanehNaftiInputInfo(models.Model):
    _name = 'sd_payaneh_nafti.input_info'
    _description = 'sd_payaneh_nafti.input_info'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'document_no'
    _rec_name = 'document_no'

    document_no = fields.Char(required=True, copy=False, readonly=True, default=lambda self: _('New'))
    loading_no = fields.Char(required=True, copy=False, readonly=True, default=lambda self: _('New'))
    loading_date = fields.Date(default=lambda self: date.today(), required=True,)
    registration_no = fields.Many2one('sd_payaneh_nafti.contract_registration', required=True,)
    buyer = fields.Many2one(related='registration_no.buyer')
    contractors = fields.Many2many(related='registration_no.contractors')
    contractor = fields.Many2one('sd_payaneh_nafti.contractors', required=True,)
    driver = fields.Char(required=True,)
    card_no = fields.Char(required=True,)
    plate_1 = fields.Many2one('sd_payaneh_nafti.plate1', required=True, string='Plate')
    plate_2 = fields.Char(required=True,)
    plate_3 = fields.Many2one('sd_payaneh_nafti.plate3', required=True,)
    plate_4 = fields.Char(required=True,)
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
    sp_gr = fields.Float(string='SP. GR.', required=True, default=0.7252)
    temperature = fields.Integer(string='Temp. (C)', required=True, default=30)
    temperature_f = fields.Float(string='Temp. (F)', compute='_temperature_f', digits=(12, 1))
    pressure = fields.Float(string='Pressure (bar)', required=True, default=2.5)
    pressure_psi = fields.Integer(compute='_pressure_psi')
    miter_no = fields.Selection([ ('1', '1'),
                                  ('2', '2'),
                                  ('3', '3'),
                                  ('4', '4'),
                                  ('5', '5'),
                                  ('6', '6'),
                                  ('7', '7'),
                                  ('8', '8'),
                                  ], required=True,)
    totalizer_start = fields.Integer(required=True,)
    totalizer_end = fields.Integer(required=True,)
    totalizer_difference = fields.Integer(required=True, compute='_totalizer_difference')
    weighbridge = fields.Selection([('no', 'No'),('yes', 'Yes')], default='no')
    tanker_empty_weight = fields.Integer(required=True,)
    tanker_full_weight = fields.Integer(required=True,)
    tanker_pure_weight = fields.Integer(required=True, compute='_tanker_pure_weight')
    evacuation_box_seal = fields.Char(required=True,)
    compartment_1 = fields.Char(required=True,)
    compartment_2 = fields.Char(required=True,)
    compartment_3 = fields.Char(required=True,)
    correction_factor = fields.Float(digits=(12, 5), required=True, default=1.0)

    api_a = fields.Float(string='API', compute='_api_a')
    ctl = fields.Float(string='CTL', digits=(12, 5), compute='_ctl_cpl')
    cpl = fields.Float(string='CPL', digits=(12, 5), compute='_ctl_cpl')
    tab_13 = fields.Float(string='TAB.13', digits=(12, 5), compute='_tab_13')
    meter_tov_l = fields.Float(string='Meter T.O.V Liter')
    meter_gsv_l = fields.Float(string='Meter G.S.V Liter')
    meter_gsv_b = fields.Float(string='Meter G.S.V BBL')
    meter_mt = fields.Float(string='Meter M.T.')
    wb_tov_l = fields.Float(string='WB T.O.V Liter')
    wb_gsv_l = fields.Float(string='WB G.S.V Liter')
    wb_gsv_b = fields.Float(string='WB G.S.V BBL')
    wb_mt = fields.Float(string='WB M.T.')
    final_tov_l = fields.Float(string='Final T.O.V Liter', compute='_finals')
    final_gsv_l = fields.Float(string='Final G.S.V Liter', compute='_finals')
    final_gsv_b = fields.Float(string='Final G.S.V BBL', compute='_finals')
    final_mt = fields.Float(string='Final M.T.', compute='_finals')

    @api.onchange('weighbridge')
    def _finals(self):
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


    @api.onchange('temperature')
    def _temperature_f(self):
        for rec in self:
            rec.temperature_f = rec.temperature * 9 / 5 + 32
    @api.onchange('sp_gr')
    def _api_a(self):
        for rec in self:
            api_a = 141.5 / rec.sp_gr - 131.5 if rec.sp_gr else 0

            rec.api_a = round(api_a, 2) if rec.registration_no.loading_type == 'internal' else round(api_a, 1)


    @api.onchange('sp_gr')
    def _tab_13(self):
        for rec in self:
            rec.tab_13 = ((141.3819577 / (rec.api_a + 131.5)) - 0.001199407795) * 0.1589872949

    @api.onchange('pressure')
    def _pressure_psi(self):
        for rec in self:
            rec.pressure_psi = rec.pressure * 14.5038

    @api.onchange('sp_gr', 'temperature', 'pressure' )
    def _ctl_cpl(self):
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
        print(f'\nk_0: {k_0}\ndelta_60: {delta_60}\nparam_b: {param_b}\n')
        print(type(self.env['ir.config_parameter'].sudo().get_param('sd_payaneh_nafti.param_b')))

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
                print(f'\nrec_pi: {rec_pi}\nrec_a: {rec_a}\nrec_b: {rec_b}\nrec_pi_star: {rec_pi_star}\nalpha_60: {alpha_60}\n  ')
            except Exception as e:
                logging.error(f'_ctl_cpl: {e}')
                print(f'_ctl_cpl: {e}')
                rec.ctl = 1
                rec.cpl = 1


    @api.onchange('weighbridge')
    def _weighbridge_change(self):
        for rec in self:
            if rec.weighbridge == 'no':
                rec.write({'tanker_empty_weight': 0, 'tanker_full_weight': 0, })

    @api.onchange('front_container', 'middle_container', 'back_container')
    def _total(self):
        for rec in self:
            rec.total = rec.front_container + rec.middle_container + rec.back_container


    @api.onchange('totalizer_end', 'totalizer_start')
    def _totalizer_difference(self):
        for rec in self:
            rec.totalizer_difference = rec.totalizer_end - rec.totalizer_start

    @api.onchange('tanker_full_weight', 'tanker_empty_weight')
    def _tanker_pure_weight(self):
        for rec in self:
            rec.tanker_pure_weight = rec.tanker_full_weight - rec.tanker_empty_weight

    @api.onchange('plate_2')
    def _plate2(self):
        a = self.plate_2
        if a and (not a.isdigit() or ( a.isdigit() and (int(a) > 1000 or int(a) < 111))):
            raise ValidationError(_('Not acceptable'))

    @api.onchange('plate_4')
    def _plate4(self):
        a = self.plate_4
        if a and (not a.isdigit() or ( a.isdigit() and (int(a) > 100 or int(a) < 11))):
            raise ValidationError(_('Not acceptable'))

    @api.constrains('document_no')
    def _check_document_no_unique(self):
        record_count = self.search_count([('document_no', '=', self.document_no),
                                           ('id', '!=', self.id)])
        if record_count > 0:
            raise ValidationError("Record already exists!")
    @api.model
    def create(self, vals):
        if vals.get('document_no', _('New')) == _('New'):
            vals['document_no'] = self.env['ir.sequence'].next_by_code('sd_payaneh_nafti.input_info') or _('New')

            vals['loading_no'] = str(jdatetime.date.today().year) + f"/{int(vals['document_no']):07d}"
        return super(SdPayanehNaftiInputInfo, self).create(vals)
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


