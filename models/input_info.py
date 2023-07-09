# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
# import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
from colorama import Fore

class SdPayanehNaftiInputInof(models.Model):
    _name = 'sd_payaneh_nafti.input_info'
    _description = 'sd_payaneh_nafti.input_info'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'document_no'
    _rec_name = 'document_no'

    document_no = fields.Char(required=True,)
    loading_no = fields.Char(required=True,)
    loading_date = fields.Date(default=lambda self: date.today() ,required=True,)
    registration_no = fields.Many2one('sd_payaneh_nafti.contract_registration', required=True,)
    carrier = fields.Char(required=True,)
    buyer = fields.Many2one(related='registration_no.buyer')
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
    sp_gr = fields.Char(string='SP. GR.', required=True,)
    temperature = fields.Char(string='Temp. (C)', required=True,)
    pressure = fields.Char(string='Pressure (bar)', required=True,)
    weighbridge = fields.Selection([('no', 'No'),('yes', 'Yes')], default='no')
    miter_no = fields.Selection([ ('1', '1'),
                                  ('2', '2'),
                                  ('3', '3'),
                                  ('4', '4'),
                                  ('5', '5'),
                                  ('6', '6'),
                                  ('7', '7'),
                                  ('8', '8'),
                                  ], required=True,)
    totalizer_start = fields.Char(required=True,)
    totalizer_end = fields.Char(required=True,)
    totalizer_difference = fields.Char(required=True,)
    shipper_empty_weight = fields.Char(required=True,)
    evacuation_box_seal = fields.Char(required=True,)
    compartment_1 = fields.Char(required=True,)
    compartment_2 = fields.Char(required=True,)
    compartment_3 = fields.Char(required=True,)

    def _total(self):
        for rec in self:
            rec.total = rec.front_container + rec.middle_container + rec.back_container

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


