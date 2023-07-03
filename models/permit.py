# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta, date
# import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from colorama import Fore

class SdPayanehNaftiPermit(models.Model):
    _name = 'sd_payaneh_nafti.permit'
    _description = 'sd_payaneh_nafti.permit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'record_date'

    def _reporter_domain(self):
        payaneh_partners = self.env['res.partner'].search([])
        payaneh_partners = [2, 10, 6, 7]
        return [('id', 'in', payaneh_partners)]

    def _project_domain(self):
        partner_id = self.env.user.partner_id
        projects = self.env['sd_payaneh_nafti.project'].search(['|',
                                                      ('payaneh_managers', 'in', partner_id.id),
                                                      ('payaneh_officers', 'in', partner_id.id),])
        return [('id', 'in', projects.ids)]

    # todo: In case you have changed the project contractor, this domain would have not updated.
    @api.onchange('project')
    def _contractor_d(self):
        self.contractor = False
        return {'domain': {'contractor': [('id', 'in', self.project.contractors.ids)]}}

    def _contractor_domain(self):
        self.contractor = False
        domain = [('id', 'in', [])]
        if self.project:
            domain = [('id', 'in', self.project.contractors.ids)]
        return domain

    permit_state = fields.Selection(
            [('open', 'Open'), ('close', 'Close'), ],
            tracking=True, copy=False, default='open', required=True,
             )

    permit_no = fields.Char(required=True, tracking=True)
    record_date = fields.Date(default=lambda self: datetime.today(), tracking=True, required=True)
    due_date = fields.Date(default=lambda self: datetime.today() + timedelta(days=3), tracking=True, required=True)
    record_type = fields.Many2one('sd_payaneh_nafti.permit.types', )
    location_des = fields.Char()
    project = fields.Many2one('sd_payaneh_nafti.project', ondelete='restrict',
                              domain=lambda self: self._project_domain(), tracking=True, required=True,
                              default=lambda self: self.project.search(['|', ('payaneh_managers', 'in', self.env.user.partner_id.id),
                                                                        ('payaneh_officers', 'in', self.env.user.partner_id.id)], limit=1))

    contractor = fields.Many2one('res.partner', domain=lambda self: self._contractor_domain(), tracking=True,)
    assignee = fields.Many2one('res.partner', 'assignee', tracking=True)

    old_record = fields.Boolean(compute='_compute_old_record')
    over_due = fields.Integer(compute='_compute_over_due', default=0)


    def _compute_old_record(self):
        for rec in self:
            rec.old_record = rec.create_date > datetime.now() - timedelta(hours=5)

    def _compute_over_due(self):
        for rec in self:
            rec.over_due = 0
            if rec.permit_state == 'open':
                if date.today() >= rec.due_date:
                    rec.over_due = 1
                elif date.today() + timedelta(days=2) >= rec.due_date:
                    rec.over_due = 2

    @api.constrains('permit_no')
    def _check_anomaly_no_unique(self):
        record_count = self.search_count([('permit_no', '=', self.permit_no),
                                           ('id', '!=', self.id)])
        if record_count > 0:
            raise ValidationError(_("Permit Number already exists!"))




class SdPayanehNaftiPermitTypes(models.Model):
    _name = 'sd_payaneh_nafti.permit.types'
    _description = 'sd_payaneh_nafti.permit.types'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer()
