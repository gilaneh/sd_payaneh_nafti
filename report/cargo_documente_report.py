# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import pytz
import jdatetime


# ########################################################################################
class ReportSdPayanehNaftiCargoDocument(models.AbstractModel):
    _name = 'report.sd_payaneh_nafti.cargo_document_report_template'
    _description = 'Cargo Document'

    # ########################################################################################
    @api.model
    def _get_report_values(self, docids, data=None):
        errors = []
        form_data = data.get('form_data')
        context = self.env.context
        time_z = pytz.timezone(context.get('tz'))
        date_time = datetime.now(time_z)
        # date_time = self.date_converter(date_time, context.get('lang'))
        document_no = form_data.get('document_no')[1]
        calendar = form_data.get('calendar')

        input_record = self.env['sd_payaneh_nafti.input_info'].search([('document_no', '=', int(document_no))])
        issue_date = input_record.loading_date
        print(f'\n {form_data.get("calendar")}')
        if calendar == 'fa_IR':
            issue_date = jdatetime.date.fromgregorian(date=issue_date).strftime('%Y/%m/%d')
        tanker_no = {'plate_1': input_record.plate_1.name,
                     'plate_2': input_record.plate_2,
                     'plate_3': input_record.plate_3.name,
                     'plate_4': input_record.plate_4,
                     }
        driver = input_record.driver

        driver_promis = f'اینجانب {driver} متعهد می شوم محموله مذکور را طبق مشخصات بالا تحویل گرفته و به مقصد برسانم در صورت کسری ،انحراف وجابه جایی و هرگونه تخلف دیگر بنابر تشخیص شرکت موظف به پرداخت خسارت و جرائم تعیین شده می باشم و بدینوسیله حق هرگونه ادعا و یا اعتراض در هر زمینه را از خود سلب می نمایم.    \n                 امضااینجانب {driver} متعهد می شوم محموله مذکور را طبق مشخصات بالا تحویل گرفته و به مقصد برسانم در صورت کسری ،انحراف وجابه جایی و هرگونه تخلف دیگر بنابر تشخیص شرکت موظف به پرداخت خسارت و جرائم تعیین شده می باشم و بدینوسیله حق هرگونه ادعا و یا اعتراض در هر زمینه را از خود سلب می نمایم.                     امضا'


        doc_data = {
            'buyer': str(input_record.buyer.buyer),
            'contractor': str(input_record.buyer.contractor),
            'contract_no': str(input_record.buyer.contract_no),
            'destination': str(input_record.registration_no.destination),
            'user_name': self.env.user.name,
            'tanker_no': tanker_no,
            'driver': driver,
            'driver_promis': driver_promis,
            'contract_type': input_record.registration_no.contract_type,
            'cargo_type': input_record.registration_no.cargo_type.name,
            'issue_date': issue_date,

            'front_container': input_record.front_container,
            'middle_container': input_record.middle_container,
            'back_container': input_record.back_container,
            'total': input_record.total ,
            'loading_no': input_record.loading_no,
        }

        # [DATE] ############
        # calendar = form_data.get('calendar')
        # start_date = form_data.get('start_date') if 'start_date' in form_data.keys() else False
        # date_format = '%Y-%m-%d'
        # start_date = datetime.strptime(start_date, date_format).date()
        # record_date = self.date_converter(start_date, calendar)['date']
        #




        company_logo = f'/web/image/res.partner/{1}/image_128/'


        return {
            'doc_ids': docids,
            'doc_model': 'sd_payaneh_nafti.input_inof',
            'document_no': document_no,
            'doc_data': doc_data,
            'input_record': input_record,
            #
            # 'errors': errors,
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