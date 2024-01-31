# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import pytz
import jdatetime
from odoo import http
import logging
import json


# ########################################################################################
class ReportSdPayanehNaftiContractDailyXlsReport(models.AbstractModel):
    _name = 'report.sd_payaneh_nafti.contract_daily_xls_report_template'
    _inherit = 'report.report_xlsx.abstract'

        # ########################################################################################
    def generate_xlsx_report(self, workbook, data, p):
        self.create_excel(workbook, self.process_data(data))

        # ########################################################################################
    def process_data(self, data):
        errors = []
        docids = []
        doc_data_list = []
        PAGE_LINES = 25
        context = self.env.context
        time_z = pytz.timezone(context.get('tz'))
        date_time = datetime.now(time_z)
        calendar = context.get('lang')
        date_time = self.date_converter(date_time, context.get('lang'))
        form_data = data.get('form_data')
        loading_type = form_data.get('loading_type')

        if docids:
            contract_record = self.env['sd_payaneh_nafti.contract_registration'].browse(docids)
            # contract_no = input_record.contract_no
            calendar = context.get('lang')
        else:
            registration_no = form_data.get('registration_no')[1]
            contract_record = self.env['sd_payaneh_nafti.contract_registration'].search(
                [('registration_no', '=', registration_no)])
            # calendar = form_data.get('calendar')
            docids = [contract_record.id]
        # REPORT DATE
        calendar = context.get('lang')
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

        input_records = self.env['sd_payaneh_nafti.input_info'].search([('registration_no', '=', registration_no)],
                                                                       order='id')
        if len(input_records) == 0:
            print(f'''
                    No record have found for contract {registration_no} on selected date: {s_start_date}
        ''')
            return {
                'errors': [_(f'No record have found for contract {registration_no} on selected date: {s_start_date} ')],
            }

        input_records_behind_date = tuple(filter(lambda rec: rec.loading_date <= report_day, input_records))
        registration = input_records[0].registration_no
        if loading_type == 'internal':
            unit = dict(registration._fields['unit']._description_selection(self.env)).get(registration.unit)
        else:
            unit = registration.unit
        #     todo: it shows metric_tone which needed to show Metric Tone

        # print(f'>>>>>>>>>\n unit: {unit} registration.unit: {registration.unit} '
        #       f'\n {registration._fields["unit"]}')

        if registration.unit == 'barrel':
            used_amounts = sum([ua.final_gsv_b for ua in input_records_behind_date])
        elif registration.unit == 'metric_ton':
            used_amounts = sum([ua.final_mt for ua in input_records_behind_date])
        else:
            used_amounts = 0
        used_amounts = int(used_amounts)
        amount = registration.amount if registration.init_amount == 0 else registration.init_amount
        remain_amounts = int(amount - used_amounts)
        # print(f'=========>  \n registration: {registration} '
        #                   f'\n len, input_records_behind_date: {len(input_records_behind_date)}'
        #                   f'\n registration.unit: {registration.unit}'
        #                   f'\n amount: {amount}'
        #                   f'\n remain_amount: {remain_amounts}'
        #                   f'\n used_amounts: {used_amounts}'
        #                   f'\n ')

        input_records_day = tuple(filter(lambda rec: rec.loading_date == report_day, input_records))
        # print(f'\n input_records: {len(input_records)} \n {input_records} \ninput_records_day {len(input_records_day)}\n {input_records_day}\n')
        inputs_list = []
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
            inputs = input_records_day[index * PAGE_LINES:(index + 1) * PAGE_LINES]
            totalizer_diff_sum = sum([_input.totalizer_difference for _input in inputs if _input.weighbridge == 'no'])
            final_tov_l_sum = sum([_input.final_tov_l for _input in inputs])
            final_gsv_l_sum = sum([_input.final_gsv_l for _input in inputs])
            final_gsv_b_sum = sum([int(_input.final_gsv_l / 158.987) for _input in inputs])
            final_mt_sum = sum([_input.final_mt for _input in inputs])
            page = {
                'totalizer_diff_sum': totalizer_diff_sum,
                'final_tov_l_sum': int(final_tov_l_sum),
                'final_gsv_l_sum': int(final_gsv_l_sum),
                'final_gsv_b_sum': int(final_gsv_b_sum),
                'final_mt_sum': final_mt_sum,
            }
            total['totalizer_diff_sum'] += totalizer_diff_sum
            total['final_tov_l_sum'] += int(final_tov_l_sum)
            total['final_gsv_l_sum'] += int(final_gsv_l_sum)
            total['final_gsv_b_sum'] += int(final_gsv_b_sum )
            total['final_mt_sum'] += final_mt_sum
            inputs_list.append(inputs)
            pages.append(page)

        doc_data = {
            'page_lines': PAGE_LINES,
            'inputs': inputs_list,
            'unit': unit,
            'remain_amounts': remain_amounts,
            'used_amounts': used_amounts,
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
            'report_date': s_start_date,
            'loading_type': loading_type,
            'doc_data_list': doc_data_list,
            'errors': errors,
        }

    def create_excel(self, workbook, report_data ):
        if report_data.get('errors'):
            raise ValidationError(report_data['errors'])
        sheet = workbook.add_worksheet(f'گزارش روزانه قرارداد')
        bold = workbook.add_format({'bold': True})
        center = workbook.add_format({'align': 'center'})
        right = workbook.add_format({'align': 'right'})
        bold_center = workbook.add_format({'bold': True,
                                           'size': 9,
                                           'align': 'center',
                                           'bg_color': '#bbbbbb',
                                           })
        format_left_to_right = workbook.add_format({"reading_order": 1})
        format_right_to_left = workbook.add_format({"reading_order": 2})
        num_format_3 = workbook.add_format({"num_format": '0.000'})
        num_format_3_bold = workbook.add_format({"num_format": '0.000','bold': True,})
        num_format_4 = workbook.add_format({"num_format": '0.0000'})
        num_format_4_bold = workbook.add_format({"num_format": '0.0000','bold': True,})
        sheet.set_column('A:Z', 10)
        sheet.set_column('B:B', 15)
        sheet.set_column('W:W', 15)
        sheet.right_to_left()
        sheet.write(0, 2, 'گزارش روزانه بارگیری نفتكش هاي زمینی میعانات گازی', bold)
        sheet.write(1, 2, report_data['report_date'], bold)
        row= 5
        sheet.write(row, 2, 'خریدار:', bold)
        # sheet.write(row, 2, 'خریدار:', bold)

        col = 0
        row = 10

        col_index = 1
        doc_data = report_data.get('doc_data_list')[0][1]
        inputs = doc_data.get('inputs')
        pages_footer = doc_data.get('pages')
        page_count = doc_data.get('page_count')
        total = doc_data.get('total')

        for index, page_data in enumerate(inputs):
            sheet.write(row, col, f'page {index + 1} of {len(inputs)}' )
            row += 1
            for r in range(row, row + 3):
                for c in range(col, col + 23):
                    sheet.write(r, c, '', bold_center)
            sheet.write(row, col, 'ردیف', bold_center)
            sheet.write(row, col + 1, 'پلاک', bold_center)
            sheet.write(row, col + 2, 'مخزن', bold_center)
            sheet.write(row, col + 3, 'SP.GR', bold_center)
            sheet.write(row + 1, col + 3, '60/60', bold_center)
            sheet.write(row, col + 4, 'API', bold_center)
            sheet.write(row, col + 5, 'T', bold_center)
            sheet.write(row + 1, col + 5, '(C)', bold_center)
            sheet.write(row, col + 6, 'T', bold_center)
            sheet.write(row + 1, col + 6, '(F)', bold_center)
            sheet.write(row, col + 7, 'P', bold_center)
            sheet.write(row + 1, col + 7, '(بار)', bold_center)
            sheet.write(row, col + 8, 'P', bold_center)
            sheet.write(row + 1, col + 8, '(PSI)', bold_center)
            sheet.write(row, col + 9, 'نوع', bold_center)
            sheet.write(row + 1, col + 9, 'بارگیری', bold_center)
            sheet.write(row, col + 10, 'میتر', bold_center)
            sheet.write(row, col + 11, 'توالایزر آغازین', bold_center)
            sheet.write(row + 1, col + 11, 'وزن خالی نفتکش', bold_center)
            sheet.write(row, col + 12, 'توالایزر پایانی', bold_center)
            sheet.write(row + 1, col + 12, 'وزن پر نفتکش', bold_center)
            sheet.write(row, col + 13, 'اختلاف توتالایزر', bold_center)
            sheet.write(row + 1, col + 13, 'وزن خالص', bold_center)
            sheet.write(row, col + 14, 'K-FACTOR', bold_center)
            sheet.write(row, col + 15, 'C.T.L 6A', bold_center)
            sheet.write(row, col + 16, 'C.P.L 6A', bold_center)
            sheet.write(row, col + 17, 'T.O.V', bold_center)
            sheet.write(row + 1, col + 17, '(Litter) ', bold_center)
            sheet.write(row + 2, col + 17, '60C ', bold_center)
            sheet.write(row, col + 18, 'G.S.V', bold_center)
            sheet.write(row + 1, col + 18, '(Litter)', bold_center)
            sheet.write(row + 2, col + 18, '60C', bold_center)
            sheet.write(row, col + 19, 'G.S.V', bold_center)
            sheet.write(row + 1, col + 19, '(BBLS)', bold_center)
            sheet.write(row + 2, col + 19, '60C', bold_center)
            sheet.write(row, col + 20, 'TAB. 13', bold_center)
            sheet.write(row, col + 21, 'M. Tons', bold_center)
            sheet.write(row, col + 22, 'Loading No', bold_center)
            row += 3
            for line_rec in page_data:
                # print(f'>>>>>>>>>   line  \n {line_rec}')

                sheet.write(row, col, col_index, center )
                # sheet.write(row, col + 1, f'[ {line_rec.plate_2} {line_rec.plate_3} {line_rec.plate_4} ][ {line_rec.plate_1} ]', format_right_to_left)
                sheet.write(row, col + 1, f'[ {line_rec.plate_1} ] [ {line_rec.plate_2} {line_rec.plate_3} {line_rec.plate_4} ]',)
                sheet.write(row, col + 2, line_rec.centralized_container, center)
                sheet.write(row, col + 3, line_rec.sp_gr, center)
                sheet.write(row, col + 4, line_rec.api_a, center)
                sheet.write(row, col + 5, line_rec.temperature, center)
                sheet.write(row, col + 6, line_rec.temperature_f, center)
                sheet.write(row, col + 7, line_rec.pressure, center)
                sheet.write(row, col + 8, line_rec.pressure_psi, center)
                sheet.write(row, col + 9, 'باسکول' if line_rec.weighbridge == 'yes' else 'میتر', center)
                sheet.write(row, col + 10, '#' if line_rec.weighbridge == 'yes' else line_rec.meter_no, center)
                sheet.write(row, col + 11, line_rec.tanker_empty_weight if line_rec.weighbridge == 'yes' else line_rec.totalizer_start, )
                sheet.write(row, col + 12, line_rec.tanker_full_weight if line_rec.weighbridge == 'yes' else line_rec.totalizer_end, )
                sheet.write(row, col + 13, line_rec.tanker_pure_weight if line_rec.weighbridge == 'yes' else line_rec.totalizer_difference, )
                sheet.write_number(row, col + 14, line_rec.correction_factor, num_format_4 )
                sheet.write(row, col + 15, round(line_rec.ctl, 5) )
                sheet.write(row, col + 16, round(line_rec.cpl, 5) )
                sheet.write(row, col + 17, line_rec.final_tov_l, )
                sheet.write(row, col + 18, line_rec.final_gsv_l, )
                sheet.write(row, col + 19, int(line_rec.final_gsv_b), )
                sheet.write(row, col + 20, round(line_rec.tab_13, 5) )
                sheet.write_number(row, col + 21, line_rec.final_mt, num_format_3 )
                sheet.write(row, col + 22, line_rec.loading_no, )

                col_index += 1
                row += 1
            for i in range(index + 1):
                sheet.write(row, col + 8, f' جمع صفحه {i + 1} اختلاف توتالایزر از بارگیری میتر ', bold )
                sheet.write(row, col + 13, pages_footer[i].get('totalizer_diff_sum') , bold)
                sheet.write(row, col + 15, f' جمع صفحه {i + 1} ', bold )

                sheet.write(row, col + 17, pages_footer[i].get('final_tov_l_sum'), bold )
                sheet.write(row, col + 18, pages_footer[i].get('final_gsv_l_sum') , bold)
                sheet.write(row, col + 19, int(pages_footer[i].get('final_gsv_b_sum')) , bold)
                sheet.write_number(row, col + 21, pages_footer[i].get('final_mt_sum'), num_format_3_bold )
                row += 1
                if i + 1 == page_count:
                    sheet.write(row, col + 8, 'جمع كل اختلاف توتالایزر از بارگیری میتر' , bold)
                    sheet.write(row, col + 13, total.get('totalizer_diff_sum'), bold)
                    sheet.write(row, col + 15, 'جمع كل' , bold)

                    sheet.write(row, col + 17, total.get('final_tov_l_sum'), bold)
                    sheet.write(row, col + 18, total.get('final_gsv_l_sum'), bold)
                    sheet.write(row, col + 19, int(total.get('final_gsv_b_sum')), bold)
                    sheet.write_number(row, col + 21, total.get('final_mt_sum'), num_format_3_bold)


            row += 3








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
