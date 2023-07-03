# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
# import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from colorama import Fore

class SdPayanehNaftiAnomaly(models.Model):
    _name = 'sd_payaneh_nafti.anomaly'
    _description = 'sd_payaneh_nafti.anomaly'
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
        # print(f'\npartner_id:{partner_id}, projects:{projects}, [(]: {[("id", "in", projects.ids)]}')
        return [('id', 'in', projects.ids)]

    @api.onchange('project')
    def _contractor_d(self):
        self.contractor = False
        self.reporter = self.env.user.partner_id
        return {'domain': {'contractor': [('id', 'in', self.project.contractors.ids)],
                           'reporter': ['|', ('id', 'in', self.project.payaneh_managers.ids),
                                        ('id', 'in', self.project.payaneh_officers.ids)]}}

    def _contractor_domain(self):
        self.contractor = False
        domain = [('id', 'in', [])]
        if self.project:
            domain = [('id', 'in', self.project.contractors.ids)]
        return domain

    anomaly_state = fields.Selection(
            [('open', 'Open'), ('close', 'Close'), ],
            tracking=True, copy=False, default='open', required=True,
             )

    anomaly_no = fields.Char(required=True, tracking=True)
    record_date = fields.Date(default=lambda self: datetime.today(), required=True, tracking=True)
    location_des = fields.Char()
    project = fields.Many2one('sd_payaneh_nafti.project', ondelete='restrict',required=True,
                              domain=lambda self: self._project_domain(), tracking=True,
                              default=lambda self: self.project.search(['|', ('payaneh_managers', 'in', self.env.user.partner_id.id),
                                                                        ('payaneh_officers', 'in', self.env.user.partner_id.id)], limit=1))
    contractor = fields.Many2one('res.partner', domain=lambda self: self._contractor_domain(), tracking=True,)
    risk_level = fields.Many2one('sd_payaneh_nafti.anomaly.risk_level', tracking=True, ondelete='restrict', required=True,
                                 default=lambda self: self.risk_level.search([('sequence', '=', 1)]) or False)
    ua_uc = fields.Selection([('unsafe_act', 'Unsafe Act'),
                              ('unsafe_condition', 'Unsafe Condition'),
                              ('health', 'Health'),
                              ('environment', 'Environment'),
                              ], default='unsafe_act', tracking=True, required=True)
    assignee = fields.Many2one('res.partner', 'assignee', tracking=True)
    description = fields.Char()


    activity = fields.Char()
    has_attach = fields.Boolean()
    contract = fields.Many2one('res.partner')
    record_type = fields.Many2one('sd_payaneh_nafti.anomaly.types')
    suggestion = fields.Text()
    action_report = fields.Text()
    due_date = fields.Date(default=lambda self: datetime.today())
    reporter = fields.Many2one('res.partner', default=lambda self: self.env.user.partner_id.id,
                               domain=lambda self: self._reporter_domain())
    old_record = fields.Boolean(compute='_compute_old_record')

    def _compute_old_record(self):
        for rec in self:
            rec.old_record = rec.create_date > datetime.now() - timedelta(hours=5)

    @api.constrains('anomaly_no')
    def _check_anomaly_no_unique(self):
        record_count = self.search_count([('anomaly_no', '=', self.anomaly_no),
                                           ('id', '!=', self.id)])
        if record_count > 0:
            raise ValidationError(_("Anomaly Number already exists!"))

    def write(self, vals):
        if len(vals) == 1 and vals.get('anomaly_state') == 'close':
            pass
        elif not self.env.user.has_group('base.group_system')  \
                and not self.env.user.partner_id in self.project.payaneh_managers \
                and self.create_date < datetime.now() - timedelta(hours=5):
            raise UserError(_('This record is not editable now.\n Only project Payaneh Manager can edit it.'))

        return super(SdPayanehNaftiAnomaly, self).write(vals)




class SdPayanehNaftiAnomalyTypes(models.Model):
    _name = 'sd_payaneh_nafti.anomaly.types'
    _description = 'sd_payaneh_nafti.anomaly.types'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer()


class SdPayanehNaftiAnomalyRiskLevel(models.Model):
    _name = 'sd_payaneh_nafti.anomaly.risk_level'
    _description = 'sd_payaneh_nafti.anomaly.risk_level'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer()