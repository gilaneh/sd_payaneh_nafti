# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
# import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from colorama import Fore

class SdPayanehNaftiTraining(models.Model):
    _name = 'sd_payaneh_nafti.training'
    _description = 'sd_payaneh_nafti.training'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'record_date'

    def _project_domain(self):
        partner_id = self.env.user.partner_id
        projects = self.env['sd_payaneh_nafti.project'].search(['|',
                                                      ('payaneh_managers', 'in', partner_id.id),
                                                      ('payaneh_officers', 'in', partner_id.id),])
        # print(f'\npartner_id:{partner_id}, projects:{projects}, [(]: {[("id", "in", projects.ids)]}')
        return [('id', 'in', projects.ids)]

    record_date = fields.Date(default=lambda self: datetime.today(), tracking=True, required=True)
    project = fields.Many2one('sd_payaneh_nafti.project', ondelete='restrict', required=True,
                              domain=lambda self: self._project_domain(), tracking=True,
                              default=lambda self: self.project.search(
                                  ['|', ('payaneh_managers', 'in', self.env.user.partner_id.id),
                                   ('payaneh_officers', 'in', self.env.user.partner_id.id)], limit=1))

    record_type = fields.Many2one('sd_payaneh_nafti.training.types', required=True,
                           ondelete='restrict',
                           default=lambda self: self.env['sd_payaneh_nafti.training.types'].search([], limit=1) or False)
    name = fields.Char()
    participants = fields.Integer()
    hours = fields.Integer()
    minutes = fields.Integer()
    man_hours = fields.Float(compute='_compute_man_hours')

    def _compute_man_hours(self):
        for rec in self:
            hours = rec.hours + rec.minutes / 60
            rec.man_hours = rec.participants * hours

class SdPayanehNaftiTrainingTypes(models.Model):
    _name = 'sd_payaneh_nafti.training.types'
    _description = 'sd_payaneh_nafti.training.types'
    _order = 'sequence'

    name = fields.Char(required=True,)
    sequence = fields.Integer(default=10)

