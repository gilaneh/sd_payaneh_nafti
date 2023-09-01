# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import pytz
import jdatetime
from odoo import http


# ########################################################################################
class ReportSdPayanehNaftiMeterReport(models.AbstractModel):
    _name = 'report.sd_payaneh_nafti.meter_report_template'
    _description = 'Meter Report'

    # ########################################################################################
    @api.model
    def _get_report_values(self, docids, data=None):
        errors = []
        context = self.env.context
        calendar = context.get('lang')

        time_z = pytz.timezone(context.get('tz'))
        date_time = datetime.now(time_z)
        date_time = self.date_converter(date_time, context.get('lang'))
        form_data = data.get('form_data')

        report_date = form_data.get('report_date')

        meter_data = self.env['sd_payaneh_nafti.meter_data'].search([('report_date', '=', report_date)], order='meter')
        meter_amount_sum = sum(list([m.meter_amounts for m in meter_data]))

        this_date_input = self.env['sd_payaneh_nafti.input_info'].search([('loading_date', '=', report_date),])
        totalizer_weighbridge_sum = sum(list([t.totalizer_difference for t in this_date_input if t.weighbridge == 'yes']))
        totalizer_sum = sum(list([t.totalizer_difference for t in this_date_input]))

        metre_weighbridget_deff = meter_amount_sum + totalizer_weighbridge_sum - totalizer_sum
        if calendar == 'fa_IR':
            report_date_show = jdatetime.date.fromgregorian(date=this_date_input[0].loading_date).strftime('%Y/%m/%d')
        return {
            'docs': this_date_input[0] if this_date_input else '',
            'doc_ids': docids,
            'doc_model': 'sd_payaneh_nafti.input_info',
            'meter_data': meter_data,
            'report_date_show': report_date_show,
            'meter_amount_sum': meter_amount_sum,
            'totalizer_weighbridge_sum': totalizer_weighbridge_sum,
            'totalizer_sum': totalizer_sum,
            'metre_weighbridget_deff': metre_weighbridget_deff,
            'errors': errors,
            }

    # ########################################################################################
    def date_converter(self, date_time, lang):
        if lang == 'fa_IR':
            date_time = jdatetime.datetime.fromgregorian(datetime=date_time)
            date_time = {'date': date_time.strftime("%Y/%m/%d"),
                  'time': date_time.strftime("%H:%M:%S")}
        else:
            date_time = {'date': date_time.strftime("%Y/%m/%d"),
                        'time': date_time.strftime("%H:%M:%S")}
        return date_time

    # ########################################################################################
    def _table_record(self, items, start_date, first_day, last_day, record_type=False):
        day = len(list([item for item in items
                        if (not record_type or item.record_type.name == record_type)
                        and item.record_date == start_date]))

        month = len(list([item for item in items
                          if (not record_type or item.record_type.name == record_type)
                          and item.record_date <= start_date
                          and item.record_date >= first_day ]))

        total = len(list([item for item in items if (not record_type or item.record_type.name == record_type)]))
        return day, month, total

    # ########################################################################################
    def _table_record_sum_of_records(self, items, start_date, first_day, last_day, record_type=False):
        day = sum(list([item.man_hours for item in items
                        if (not record_type or item.record_type.name == record_type)
                        and item.record_date == start_date]))

        month = sum(list([item.man_hours for item in items
                          if (not record_type or item.record_type.name == record_type)
                          and item.record_date <= start_date
                          and item.record_date >= first_day ]))

        total = sum(list([item.man_hours for item in items if (not record_type or item.record_type.name == record_type)]))
        day = int(round(day, 0))
        month = int(round(month, 0))
        total = int(round(total, 0))
        return day, month, total

