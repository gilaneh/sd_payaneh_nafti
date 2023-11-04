# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import pytz
import jdatetime
from odoo import http


# ########################################################################################
class ReportSdPayanehNaftiContractDailyReport(models.AbstractModel):
    _name = 'report.sd_payaneh_nafti.contract_daily_report_template'
    _description = 'Contract Daily Report'

    # ########################################################################################
    @api.model
    def _get_report_values(self, docids, data=None):
        errors = []
        doc_data_list = []
        PAGE_LINES = 25
        context = self.env.context
        time_z = pytz.timezone(context.get('tz'))
        date_time = datetime.now(time_z)
        calendar = context.get('lang')
        date_time = self.date_converter(date_time, context.get('lang'))
        form_data = data.get('form_data')
        if docids:
            contract_record = self.env['sd_payaneh_nafti.contract_registration'].browse(docids)
            # contract_no = input_record.contract_no
            calendar = context.get('lang')
        else:
            registration_no = form_data.get('registration_no')[1]
            contract_record = self.env['sd_payaneh_nafti.contract_registration'].search([('registration_no', '=', registration_no)])
            # calendar = form_data.get('calendar')
            docids = [contract_record.id]
        # REPORT DATE

        report_date = form_data.get('report_date') if 'report_date' in form_data.keys() else False
        date_format = '%Y-%m-%d'
        report_date = datetime.strptime(report_date, date_format).date()

        if calendar == 'fa_IR':
            first_day = jdatetime.date.fromgregorian(date=report_date).replace(day=1)
            next_month = first_day.replace(day=28) + timedelta(days=5)
            last_day = (next_month - timedelta(days=next_month.day)).togregorian()
            first_day = first_day.togregorian
            report_day = report_date
            # report_date = jdatetime.date.fromgregorian(date=report_date).strftime('%Y/%m/%d')
            s_start_date = jdatetime.date.fromgregorian(date=report_date).strftime("%Y/%m/%d")

        else:
            first_day = report_date.replace(day=1)
            next_month = first_day.replace(day=28) + timedelta(days=5)
            last_day = next_month - timedelta(days=next_month.day)
            report_day = report_date
            s_start_date = report_date.strftime("%Y/%m/%d")





        input_records = self.env['sd_payaneh_nafti.input_info'].search([('registration_no', '=', registration_no)], order='id')
        if len(input_records) == 0:
            return {
                'errors': [_(f'No record have found for contract {registration_no} on selected date: {s_start_date} ')],
            }
        input_records_day = tuple(filter(lambda rec: rec.loading_date == report_day, input_records))
        # print(f'\n input_records: {len(input_records)} \n {input_records} \ninput_records_day {len(input_records_day)}\n {input_records_day}\n')
        inputs = []
        pages = []
        total = {
            'totalizer_diff_sum': 0,
            'final_tov_l_sum': 0,
            'final_gsv_l_sum': 0,
            'final_gsv_b_sum': 0,
            'final_mt_sum': 0,
        }
        page_count = len(input_records_day) // PAGE_LINES + 1
        for index in range(page_count):
            input = input_records_day[index * PAGE_LINES:(index + 1) * PAGE_LINES]
            totalizer_diff_sum = sum([input.totalizer_difference for input in input if input.weighbridge == 'no'])
            final_tov_l_sum = sum([input.final_tov_l for input in input])
            final_gsv_l_sum = sum([input.final_gsv_l for input in input])
            final_mt_sum = sum([input.final_mt for input in input])
            page = {
                'totalizer_diff_sum': totalizer_diff_sum,
                'final_tov_l_sum': int(final_tov_l_sum),
                'final_gsv_l_sum': int(final_gsv_l_sum),
                'final_gsv_b_sum': final_gsv_l_sum/158.987,
                'final_mt_sum': final_mt_sum,
            }
            total['totalizer_diff_sum'] += totalizer_diff_sum
            total['final_tov_l_sum'] += int(final_tov_l_sum)
            total['final_gsv_l_sum'] += int(final_gsv_l_sum)
            total['final_gsv_b_sum'] += final_gsv_l_sum/158.987
            total['final_mt_sum'] += final_mt_sum
            inputs.append(input)
            pages.append(page)





        doc_data = {
                    'page_lines': PAGE_LINES,
                    'inputs': inputs,
                    'pages': pages,
                    'total': total,
                    'page_count': page_count,
                    'input_records_day': input_records_day,
                    'payaneh_agent': form_data.get('payaneh_agent'),
                    'observe_agent': form_data.get('observe_agent'),
                    'buyer_agent': form_data.get('buyer_agent')
                    }
        doc_data_list.append((contract_record, doc_data))




        company_logo = f'/web/image/res.partner/{1}/image_128/'
        return {
            'docs': contract_record,
            'doc_ids': docids,
            'doc_model': 'sd_payaneh_nafti.input_info',
            'report_date': report_date,
            'doc_data_list': doc_data_list,
            # 'input_record': input_record,
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

