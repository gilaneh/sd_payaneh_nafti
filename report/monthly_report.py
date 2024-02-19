# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import pytz
import jdatetime
from odoo import http


# ########################################################################################
class ReportSdPayanehNaftiMonthly(models.AbstractModel):
    _name = 'report.sd_payaneh_nafti.monthly_report_template'
    _description = 'Monthly Report'

    # ########################################################################################
    @api.model
    def _get_report_values(self, docids, data=None):
        errors = []
        doc_data_list = []
        row_data_lines = []
        # context = self.env.context
        # time_z = pytz.timezone(context.get('tz'))
        # date_time = datetime.now(time_z)
        # date_time = self.date_converter(date_time, context.get('lang'))
        #
        # form_data = data.get('form_data')
        # start_date = form_data.get('start_date')
        # date_format = '%Y-%m-%d'
        # start_date = datetime.strptime(start_date, date_format).date()
        # calendar = form_data.get('calendar')
        #
        # if calendar == 'fa_IR':
        #     first_day = jdatetime.date.fromgregorian(date=start_date).replace(day=1)
        #     next_month = first_day.replace(day=28) + timedelta(days=5)
        #     last_day = (next_month - timedelta(days=next_month.day)).togregorian()
        #     first_day = first_day.togregorian()
        #     s_first_day = jdatetime.date.fromgregorian(date=first_day).strftime("%Y/%m/%d")
        #     s_last_day = jdatetime.date.fromgregorian(date=last_day).strftime("%Y/%m/%d")
        #
        # else:
        #     first_day = start_date.replace(day=1)
        #     next_month = first_day.replace(day=28) + timedelta(days=5)
        #     last_day = next_month - timedelta(days=next_month.day)
        #     s_first_day = first_day.strftime("%Y-%m-%d")
        #     s_last_day = last_day.strftime("%Y-%m-%d")
        calendar = self.env.context.get('lang')
        form_data = data.get('form_data')
        year = form_data.get('year')
        month = form_data.get('month')

        if calendar == 'fa_IR':
            first_day = jdatetime.date(int(year), int(month), 1)
            next_month = first_day.replace(day=28) + timedelta(days=5)
            last_day = (next_month - timedelta(days=next_month.day)).togregorian()
            first_day = first_day.togregorian()
            s_first_day = jdatetime.date.fromgregorian(date=first_day).strftime("%Y/%m/%d")
            s_last_day = jdatetime.date.fromgregorian(date=last_day).strftime("%Y/%m/%d")

        else:
            date_format = '%Y-%m-%d'
            start_date = datetime.strptime(f'{year}-{month}-1', date_format).date()
            first_day = start_date.replace(day=1)
            next_month = first_day.replace(day=28) + timedelta(days=5)
            last_day = next_month - timedelta(days=next_month.day)
            s_first_day = first_day.strftime("%Y-%m-%d")
            s_last_day = last_day.strftime("%Y-%m-%d")
        input_records = self.env['sd_payaneh_nafti.input_info'].search([('loading_date', '>=', first_day),
                                                                        ('loading_date', '<=', last_day)])
        if len(input_records) == 0:
            return{
                'errors': [_(f'No record have found for selected time duration: {s_first_day} to {s_last_day}')],
                }
        docids = [input_records.ids]


        registration_nos = sorted(list({rec.registration_no.registration_no for rec in input_records}))
        # print(f'\nregistration_codes:{registration_nos}\n')
        row_data_temp = []
        for index, reg_no in enumerate(registration_nos):
            data = [rec for rec in input_records if rec.registration_no.registration_no == reg_no]
            final_gsv_l = [rec.final_gsv_l for rec in input_records if rec.registration_no.registration_no == reg_no]
            final_gsv_b = [rec.final_gsv_b for rec in input_records if rec.registration_no.registration_no == reg_no]
            final_mt = [rec.final_mt for rec in input_records if rec.registration_no.registration_no == reg_no]
            # for d in data:
            d = data[0]
            reg = d.registration_no
            # unit = dict(reg._fields['unit']._description_selection(self.env)).get(reg.unit)
            # loading_type = dict(reg._fields['loading_type']._description_selection(self.env)).get(reg.loading_type)
            # contract_type = dict(reg._fields['contract_type']._description_selection(self.env)).get(reg.contract_type)
            unit = reg.unit
            loading_type = reg.loading_type
            contract_type = reg.contract_type

            row_data_lines.append((index + 1,
                                   d.registration_no.letter_no if d.registration_no.letter_no  else '',
                                   d.registration_no.contract_no if d.registration_no.contract_no  else '',
                                   d.registration_no.order_no if d.registration_no.order_no else '',
                                   d.registration_no.buyer.name if d.registration_no.buyer.name else '',
                                   d.registration_no.amount if d.registration_no.amount else '',
                                   unit,
                                   loading_type,
                                   contract_type,
                                   int(sum(final_gsv_l)),
                                   round(sum(final_gsv_b), 2),
                                   round(sum(final_mt), 3),
                                   len(data),

                                   ))


        final_gsv_l_stock_1 = [rec[9] for rec in row_data_lines if rec[8] == 'stock']
        print(f'''
            final_gsv_l_stock_1: {final_gsv_l_stock_1}


''')
            # final_gsv_l_stock_1: {sum(final_gsv_l_stock_1)}
        final_gsv_l_stock = [int(rec.final_gsv_l) for rec in input_records if rec.registration_no.contract_type == 'stock']
        final_gsv_l_general = [int(rec.final_gsv_l) for rec in input_records if rec.registration_no.contract_type == 'general']
        final_gsv_l_internal = [int(rec.final_gsv_l) for rec in input_records if rec.registration_no.loading_type == 'internal']
        final_gsv_l_export = [int(rec.final_gsv_l) for rec in input_records if rec.registration_no.loading_type == 'export']
        final_gsv_b_stock = [rec.final_gsv_b for rec in input_records if rec.registration_no.contract_type == 'stock']
        final_gsv_b_general = [rec.final_gsv_b for rec in input_records if rec.registration_no.contract_type == 'general']
        final_gsv_b_internal = [rec.final_gsv_b for rec in input_records if rec.registration_no.loading_type == 'internal']
        final_gsv_b_export = [rec.final_gsv_b for rec in input_records if rec.registration_no.loading_type == 'export']
        final_mt_stock = [rec.final_mt for rec in input_records if rec.registration_no.contract_type == 'stock']
        final_mt_general = [rec.final_mt for rec in input_records if rec.registration_no.contract_type == 'general']
        final_mt_internal = [rec.final_mt for rec in input_records if rec.registration_no.loading_type == 'internal']
        final_mt_export = [rec.final_mt for rec in input_records if rec.registration_no.loading_type == 'export']
        footer_data = {
            'final_gsv_l_stock': int(sum(final_gsv_l_stock)),
            'final_gsv_b_stock': round(sum(final_gsv_b_stock), 2),
            'final_mt_stock': round(sum(final_mt_stock), 3),
            'tank_count_stock': len(final_gsv_l_stock),

            'final_gsv_l_general': int(sum(final_gsv_l_general)),
            'final_gsv_b_general': round(sum(final_gsv_b_general), 2),
            'final_mt_general': round(sum(final_mt_general), 3),
            'tank_count_general': len(final_gsv_l_general),

            'final_gsv_l_internal': int(sum(final_gsv_l_internal)),
            'final_gsv_b_internal': round(sum(final_gsv_b_internal), 2),
            'final_mt_internal': round(sum(final_mt_internal), 3),
            'tank_count_internal': len(final_gsv_l_internal),

            'final_gsv_l_export': int(sum(final_gsv_l_export)),
            'final_gsv_b_export': round(sum(final_gsv_b_export), 2),
            'final_mt_export': round(sum(final_mt_export), 3),
            'tank_count_export': len(final_gsv_l_export),

        }

        # print('-' * 150)

        # print(f'| {sum(final_gsv_l_stock)}'
        #       f'| {sum(final_gsv_l_general)}'
        #       f'| {sum(final_gsv_l_internal)}'
        #       f'| {sum(final_gsv_l_export)}'
        #       )
        # print(f' | {" ": ^3}'
        #       f' | {" ": ^6}'
        #       f' | {" ": ^6}'
        #       f' | {" ": ^9}'
        #       f' | {" ": ^9}'
        #       f' | {" ": ^5}'
        #       f' | {" ": ^30}'
        #       f' | {" ": ^8}'
        #       f' | {" ": ^8}'
        #       f' | {" ": ^10}'
        #       f' | {int(sum(final_gsv_l_stock)): >10}'
        #       f' | {int(sum(final_gsv_b_stock)): >10}'
        #       f' | {int(sum(final_mt_stock)): >10}'
        #       f' | {len(final_gsv_l_stock): >3}'
        #       )
        # print(f' | {" ": ^3}'
        #       f' | {" ": ^6}'
        #       f' | {" ": ^6}'
        #       f' | {" ": ^9}'
        #       f' | {" ": ^9}'
        #       f' | {" ": ^5}'
        #       f' | {" ": ^30}'
        #       f' | {" ": ^8}'
        #       f' | {" ": ^8}'
        #       f' | {" ": ^10}'
        #       f' | {int(sum(final_gsv_l_general)): >10}'
        #       f' | {int(sum(final_gsv_b_general)): >10}'
        #       f' | {int(sum(final_mt_general)): >10}'
        #       f' | {len(final_gsv_l_general): >3}'
        #       )
        # print(f' | {" ": ^3}'
        #       f' | {" ": ^6}'
        #       f' | {" ": ^6}'
        #       f' | {" ": ^9}'
        #       f' | {" ": ^9}'
        #       f' | {" ": ^5}'
        #       f' | {" ": ^30}'
        #       f' | {" ": ^8}'
        #       f' | {" ": ^8}'
        #       f' | {" ": ^10}'
        #       f' | {int(sum(final_gsv_l_general) + sum(final_gsv_l_stock)): >10}'
        #       f' | {int(sum(final_gsv_b_general) + sum(final_gsv_b_stock)): >10}'
        #       f' | {int(sum(final_mt_general) + sum(final_mt_stock)): >10}'
        #       f' | {len(final_gsv_l_general) + len(final_gsv_l_stock): >3}'
        #       )
        # print(f' | {" ": ^3}'
        #       f' | {" ": ^6}'
        #       f' | {" ": ^6}'
        #       f' | {" ": ^9}'
        #       f' | {" ": ^9}'
        #       f' | {" ": ^5}'
        #       f' | {" ": ^30}'
        #       f' | {" ": ^8}'
        #       f' | {" ": ^8}'
        #       f' | {" ": ^10}'
        #       f' | {int(sum(final_gsv_l_internal)): >10}'
        #       f' | {int(sum(final_gsv_b_internal)): >10}'
        #       f' | {int(sum(final_mt_internal)): >10}'
        #       f' | {len(final_gsv_l_internal): >3}'
        #       )
        # print(f' | {" ": ^3}'
        #       f' | {" ": ^6}'
        #       f' | {" ": ^6}'
        #       f' | {" ": ^9}'
        #       f' | {" ": ^9}'
        #       f' | {" ": ^5}'
        #       f' | {" ": ^30}'
        #       f' | {" ": ^8}'
        #       f' | {" ": ^8}'
        #       f' | {" ": ^10}'
        #       f' | {int(sum(final_gsv_l_export)): >10}'
        #       f' | {int(sum(final_gsv_b_export)): >10}'
        #       f' | {int(sum(final_mt_export)): >10}'
        #       f' | {len(final_gsv_l_export): >3}'
        #       )





        # if len(input_record) > 1:
        #     errors.append(_('[ERROR] There is more than one record'))
        # elif len(input_record) == 1:
        # for input_record in input_records:
        #     issue_date = input_record.loading_date
        #     if calendar == 'fa_IR':
        #         issue_date = jdatetime.date.fromgregorian(date=issue_date).strftime('%Y/%m/%d')
        #     tanker_no = {'plate_1': input_record.plate_1,
        #                  'plate_2': input_record.plate_2,
        #                  'plate_3': input_record.plate_3,
        #                  'plate_4': input_record.plate_4,
        #                  }
        #     contract_no = str(input_record.registration_no.contract_no)
        #     if input_record.registration_no.order_no:
        #         contract_no += '-' + str(input_record.registration_no.order_no)
        #
        #     doc_data = {
        #                 # 'buyer': str(input_record.buyer.name),
        #                 # 'contractor': str(input_record.contractor.name),
        #                 'document_no': input_record.document_no,
        #                 'contract_no': contract_no,
        #                 'user_name': self.env.user.name,
        #                 'tanker_no': tanker_no,
        #                 'driver': input_record.driver,
        #                 'contract_type': input_record.registration_no.contract_type,
        #                 'cargo_type': input_record.registration_no.cargo_type.name,
        #                 'front_container': input_record.front_container,
        #                 'middle_container': input_record.middle_container,
        #                 'back_container': input_record.back_container,
        #                 'total': input_record.total,
        #                 'issue_date': issue_date,
        #                 'loading_no': input_record.loading_no,
        #                 }
        #     doc_data_list.append((input_record, doc_data))
        # else:
        #     input_record = []
        #     errors.append(_('[ERROR] There is no record'))
        company_logo = f'/web/image/res.partner/{1}/image_128/'
        doc_data_list = [('', '')]
        # errors = ['test error']
        return {
            'docs': input_records[0] if input_records else '',
            'doc_ids': docids,
            'doc_model': 'sd_payaneh_nafti.input_info',
            # 'document_no': document_no,
            'doc_data_list': doc_data_list,
            'row_data_lines': row_data_lines,
            'footer_data': footer_data,
            'dates': [s_first_day, s_last_day],
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

