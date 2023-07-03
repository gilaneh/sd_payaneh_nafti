# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
# import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from colorama import Fore

class SdPayanehNaftiPersonnel(models.Model):
    _name = 'sd_payaneh_nafti.personnel'
    _description = 'sd_payaneh_nafti.personnel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'record_date'

    def _project_domain(self):
        partner_id = self.env.user.partner_id
        projects = self.env['sd_payaneh_nafti.project'].search(['|',
                                                      ('payaneh_managers', 'in', partner_id.id),
                                                      ('payaneh_officers', 'in', partner_id.id),])
        # print(f'\npartner_id:{partner_id}, projects:{projects}, [(]: {[("id", "in", projects.ids)]}')
        return [('id', 'in', projects.ids)]

    record_date = fields.Date(default=lambda self: datetime.today(), tracking=True, required=True,)
    project = fields.Many2one('sd_payaneh_nafti.project', ondelete='restrict', required=True,
                              domain=lambda self: self._project_domain(), tracking=True,
                              default=lambda self: self.project.search(
                                  ['|', ('payaneh_managers', 'in', self.env.user.partner_id.id),
                                   ('payaneh_officers', 'in', self.env.user.partner_id.id)], limit=1))
    subcontractor = fields.Integer()
    contractor = fields.Integer()
    local = fields.Integer()
    client = fields.Integer()
    visitor = fields.Integer()
    total = fields.Integer(compute='_total_personnel')
    # It is not working !?
    # _sql_constraints = [('personnel_record_date_project_uniq', 'unique (record_date, project)',
    #                      "Combination of project and date already exists !")]

    @api.constrains('record_date', 'project')
    def _check_project_unique(self):
        record_count = self.search_count([('record_date', '=', self.record_date),
                                           ('project', '=', self.project.id),
                                           ('id', '!=', self.id)])
        if record_count > 0:
            raise ValidationError(_("Record already exists!"))

    @api.model
    def create(self, vals):
        return super(SdPayanehNaftiPersonnel, self).create(vals)

    @api.onchange('subcontractor', 'contractor', 'local', 'client', 'visitor')
    def _total_personnel(self):
        for rec in self:
            rec.total = rec.subcontractor + rec.contractor + rec.local + rec.client + rec.visitor
