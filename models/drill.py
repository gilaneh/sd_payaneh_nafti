# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
# import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from colorama import Fore

class SdPayanehNaftiDrill(models.Model):
    _name = 'sd_payaneh_nafti.drill'
    _description = 'sd_payaneh_nafti.drill'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'record_date'

    def _project_domain(self):
        partner_id = self.env.user.partner_id
        projects = self.env['sd_payaneh_nafti.project'].search(['|',
                                                      ('payaneh_managers', 'in', partner_id.id),
                                                      ('payaneh_officers', 'in', partner_id.id),])
        # print(f'\npartner_id:{partner_id}, projects:{projects}, [(]: {[("id", "in", projects.ids)]}')
        return [('id', 'in', projects.ids)]

    def _participants_domain(self):
        # self.participants = False
        domain = [('id', 'in', [])]
        if self.project:
            domain = [('id', 'in', self.project.contractors.ids)]
        return domain

    record_date = fields.Date(default=lambda self: datetime.today(), tracking=True, required=True)
    project = fields.Many2one('sd_payaneh_nafti.project', ondelete='restrict', required=True,
                              domain=lambda self: self._project_domain(), tracking=True,
                              default=lambda self: self.project.search(
                                  ['|', ('payaneh_managers', 'in', self.env.user.partner_id.id),
                                   ('payaneh_officers', 'in', self.env.user.partner_id.id)], limit=1))

    record_type = fields.Many2one('sd_payaneh_nafti.drill.types', required=True,
                           ondelete='restrict',
                           default=lambda self: self.env['sd_payaneh_nafti.drill.types'].search([], limit=1) or False)
    name = fields.Char(required=True,)
    location = fields.Char()
    participants = fields.Many2many('res.partner',
                                    domain=lambda self: self._participants_domain(),
                                    tracking=True, required=False)
    attendees = fields.Char()
    strengths = fields.Text()
    weaknesses = fields.Text()
    improve_actions = fields.Text()


class SdPayanehNaftiDrillTypes(models.Model):
    _name = 'sd_payaneh_nafti.drill.types'
    _description = 'sd_payaneh_nafti.drill.types'
    _order = 'sequence'

    name = fields.Char(required=True,)
    sequence = fields.Integer(default=10)

