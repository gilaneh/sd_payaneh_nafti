# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta, date
# import random

from odoo import models, fields, api

from colorama import Fore


class SdPayanehNaftiProjectPartners(models.Model):
    _name = 'sd_payaneh_nafti.project'
    _description = 'sd_payaneh_nafti.project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _order = 'sequence,id asc'

    name = fields.Char(help='It can imply project name and its construction site', required=True,)
    project = fields.Many2one('project.project', required=True,)
    payaneh_managers = fields.Many2many('res.partner', 'payaneh_managers')
    payaneh_managers_users = fields.Many2many('res.users', 'payaneh_managers_users')
    payaneh_officers = fields.Many2many('res.partner', 'payaneh_officers')
    payaneh_officers_users = fields.Many2many('res.users','payaneh_officers_users')
    contractors = fields.Many2many('res.partner', 'contractors', required=True,)
    daily_work_hours = fields.Integer()

    record_date = fields.Date(defualt=lambda self: datetime.now().date(), required=True, help='These data is sum of all from project start date untile this date')
    personnel_subcontractor = fields.Integer(string='Subcontractor')
    personnel_contractor = fields.Integer(string='Contractor')
    personnel_local = fields.Integer(string='Local')
    personnel_client = fields.Integer(string='Client')

    fatality = fields.Integer()
    ptd_ppd = fields.Integer(string='PTD&PPD')
    lti = fields.Integer(string='LTI')
    rwc = fields.Integer(string='RWC')
    illness = fields.Integer(string='illness')
    mtc = fields.Integer(string='MTC')
    audits = fields.Integer()
    ua_uc = fields.Integer(string='UA/UC')
    near_miss = fields.Integer()
    meetings = fields.Integer()
    training = fields.Integer()
    fac = fields.Integer(string='FAC')
    rva = fields.Integer(string='RVA')
    fire = fields.Integer()
    prdc = fields.Integer(string='PRDC')
    medical_rest = fields.Integer()
    total_personnel = fields.Integer(string='Total', compute='_total_personnel')

    @api.onchange('personnel_subcontractor', 'personnel_contractor', 'personnel_local', 'personnel_client')
    def _total_personnel(self):
        for rec in self:
            rec.total_personnel = rec.personnel_subcontractor + rec.personnel_contractor + rec.personnel_local + rec.personnel_client

    def write(self, vals):
        print(vals)
        payaneh_managers_ids = []
        payaneh_officers_ids = []
        payaneh_ids = []
        if vals.get('payaneh_managers') and vals.get('payaneh_managers')[0][0] == 6:
            payaneh_managers_ids = vals.get('payaneh_managers')[0][2]
        else:
            payaneh_managers_ids = self.payaneh_managers.ids
        users = self.env['res.users'].search([('partner_id', 'in', payaneh_managers_ids)])
        vals['payaneh_managers_users'] = users

        if vals.get('payaneh_officers') and vals.get('payaneh_officers')[0][0] == 6:
            payaneh_officers_ids = vals.get('payaneh_officers')[0][2]
        else:
            payaneh_officers_ids = self.payaneh_officers.ids
        users = self.env['res.users'].search([('partner_id', 'in', payaneh_officers_ids)])
        vals['payaneh_officers_users'] = users


        print(Fore.RED, payaneh_managers_ids, payaneh_officers_ids, self.payaneh_managers_users, self.payaneh_officers_users, Fore.RESET)
        return super(SdPayanehNaftiProjectPartners, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('payaneh_managers') and vals.get('payaneh_managers')[0][0] == 6:
            payaneh_managers_ids = vals.get('payaneh_managers')[0][2]
            users = self.env['res.users'].search([('partner_id', 'in', payaneh_managers_ids)])
            vals['payaneh_managers_users'] = users

        if vals.get('payaneh_officers') and vals.get('payaneh_officers')[0][0] == 6:
            payaneh_officers_ids = vals.get('payaneh_officers')[0][2]
            users = self.env['res.users'].search([('partner_id', 'in', payaneh_officers_ids)])
            vals['payaneh_officers_users'] = users
        print(Fore.RED, payaneh_managers_ids, payaneh_officers_ids, self.payaneh_managers_users, self.payaneh_officers_users,
                  Fore.RESET)

        return super(SdPayanehNaftiProjectPartners, self).create(vals)
            