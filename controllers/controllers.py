# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
import datetime
from colorama import Fore
import jdatetime


class Apps(http.Controller):
    @http.route('/apps/', type='http', auth="public", website=True)
    # @http.route('/sd_payaneh_nafti/attendance/', type='http', auth="public", methods=['GET'], website=True)
    def sd_payaneh_nafti_http(self, **kwargs):
        time_1 = datetime.datetime.now()
        # todo: timezone
        today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=4.5)

        # todo: localized search results based on user's ip address (tehran user might has seed the tehran users first)
        if kwargs.get('search'):
            search = kwargs.get('search')
            if search == '':
                search = 0
        else:
            search = 0




        if search:
            #  multi word search, it can be process with 'and' or 'or' operand
            list = ''.join(search).split()
            apps = http.request.env['sd_payaneh_nafti.settings'].sudo().search(['|',
                                                                       ('name', 'like', list[0]),
                                                                       ('link', 'like', list[0]),
                                                                       ],order='priority,name asc')
            for item in list[1::]:
                apps = http.request.env['sd_payaneh_nafti.settings'].sudo().search(['|',
                                                                           ('name', 'like', item),
                                                                           ('link', 'like', item),
                                                                           ], order='priority,name asc')

            return self.render_http(apps,time_1, today)
        else:
            apps = http.request.env['sd_payaneh_nafti.settings'].sudo().search([], order='priority,name asc')
            return self.render_http(apps,time_1, today)





    def render_http(self,apps,time_1,today,search=''):

        time_2 = datetime.datetime.now()
        duration = round((time_2 - time_1).microseconds / 1000 , 1)
        count = len(apps)
        print(Fore.RED,count)
        print(Fore.RED,count)
        print(Fore.RED,count)
        return http.request.render('sd_payaneh_nafti.apps', {'apps': apps,
                                                    'count': count,
                                                    'search': search,
                                                    'duration': duration,})

