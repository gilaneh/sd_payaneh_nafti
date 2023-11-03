# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta
# import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from colorama import Fore
from odoo.modules.module import get_module_resource
import base64
from PIL import Image
class SdPayanehNaftiDrivers(models.Model):
    _name = 'sd_payaneh_nafti.drivers'
    _description = 'sd_payaneh_nafti.drivers'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _default_image(self):
        image_path = get_module_resource('lunch', 'static/img', 'lunch.png')
        return base64.b64encode(open(image_path, 'rb').read())

    name = fields.Char(required=True,)
    description = fields.Char()
    card_no = fields.Char()
    # image_1920 = fields.Image(default=_default_image)
    image_1920 = fields.Image()


    # todo: resizing image
    @api.onchange('image_1920')
    def image_resize(self):
        image = Image.open(self.image_1920)
        print(f"Original size : {image.size}")

        self.image_1920 = image.resize((100, 100))
        print(f"Original size : {self.image_1920.size}")