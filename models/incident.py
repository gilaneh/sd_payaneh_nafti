# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
# import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from colorama import Fore

class SdPayanehNaftiIncident(models.Model):
    _name = 'sd_payaneh_nafti.incident'
    _description = 'sd_payaneh_nafti.incident'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'record_date'

    @api.onchange('project')
    def _reporter_domain(self):
        self.reporter = self.env.user.partner_id.id
        domain = [('id', 'in', [])]
        if self.project:
            domain = ['|', ('id', 'in', self.project.payaneh_managers.ids), ('id', 'in', self.project.payaneh_officers.ids)]
            print(domain)
        return {'domain': {'reporter': domain}}

    def _project_domain(self):
        partner_id = self.env.user.partner_id
        projects = self.env['sd_payaneh_nafti.project'].search(['|',
                                                      ('payaneh_managers', 'in', partner_id.id),
                                                      ('payaneh_officers', 'in', partner_id.id),])
        return [('id', 'in', projects.ids)]

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


    record_date = fields.Date(default=lambda self: datetime.today(), tracking=True, required=True)
    project = fields.Many2one('sd_payaneh_nafti.project', ondelete='restrict', required=True,
                              domain=lambda self: self._project_domain(), tracking=True,
                              default=lambda self: self.project.search(['|', ('payaneh_managers', 'in', self.env.user.partner_id.id),
                                                                        ('payaneh_officers', 'in', self.env.user.partner_id.id)], limit=1))
    contractor = fields.Many2one('res.partner', domain=lambda self: self._contractor_domain(), tracking=True, required=False)
    record_type = fields.Many2one('sd_payaneh_nafti.incident.types', tracking=True, ondelete='restrict', required=True,)
    description = fields.Char()
    consequence = fields.Char()
    reporter = fields.Many2one('res.partner', 'reporter',
                               default=lambda self: self.env.user.partner_id.id ,
                               domain=lambda self: self._reporter_domain(), tracking=True)
    medical_rest = fields.Integer()
    actions = fields.Text()
    old_record = fields.Boolean(compute='_compute_old_record')

    def _compute_old_record(self):
        for rec in self:
            rec.old_record = rec.create_date > datetime.now() - timedelta(hours=5)


class SdPayanehNaftiIncidentTypes(models.Model):
    _name = 'sd_payaneh_nafti.incident.types'
    _description = 'sd_payaneh_nafti.incident.types'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
