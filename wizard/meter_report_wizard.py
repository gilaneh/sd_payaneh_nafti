# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo import Command
from colorama import Fore
from datetime import datetime, date
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError
import pytz
# #############################################################################
class SdPayanehNaftiReportMeterReport(models.TransientModel):
    _name = 'sd_payaneh_nafti.report.meter_report'
    _description = 'Meter Report'

    meter_report_date = fields.Date(required=True, default=lambda self: datetime.now(pytz.timezone(self.env.context.get('tz') or 'Asia/Tehran')) )
    # meter_data = fields.Many2many('sd_payaneh_nafti.meter_data', 'meter_data_report')
    # meter_comment = fields.Many2one('sd_payaneh_nafti.meter_comments',)
    meters = fields.Html(readonly=True)
    mismatch = fields.Html(readonly=True)
    meter_comment = fields.Html()
    meter_data = fields.Char()

    # start_date = fields.Date(required=True, default=lambda self: date.today() )
    # calendar = fields.Selection([('fa_IR', 'Persian'), ('en_US', 'Gregorian')],
    #                             default=lambda self: 'fa_IR' if self.env.context.get('lang') == 'fa_IR' else 'en_US')

    # #############################################################################
    def process_report(self):
        meter_comments_model = self.env['sd_payaneh_nafti.meter_comments']
        comment = meter_comments_model.search([('comment_date', '=', self.meter_report_date)])
        if len(comment) > 0:
            comment[0].write({'comments': self.meter_comment})
        else:
            self.env['sd_payaneh_nafti.meter_comments'].create({
                'comment_date': self.meter_report_date,
                'comments': self.meter_comment
            })

        read_form = self.read()[0]
        data = {'form_data': read_form}
        xml_id = 'sd_payaneh_nafti.meter_report'
        report_action = self.env.ref(xml_id).report_action(self, data=data)
        report_action.update({'close_on_report_download': True})
        return report_action

    @api.depends('meter_report_date')
    @api.onchange('meter_report_date')
    def _report_data_changed(self):
        comment = self.env['sd_payaneh_nafti.meter_comments'].search([('comment_date', '=', self.meter_report_date)])
        if len(comment) > 0:
            self.meter_comment = comment[0].comments
        else:
            self.meter_comment = ''


        this_date_input = self.env['sd_payaneh_nafti.input_info'].search([('loading_info_date', '=', self.meter_report_date),])
        meter_no_list = [ '1', '2', '3', '4', '5', '6', '7', '8', '0']

        # create meter report preview
        meter_data = f'''
                <div class="row bg-300 text-center">
                    <div class="col-2">Meter No</div>
                    <div class="col-3">First Totalizer</div>
                    <div class="col-3">Last Totalizer</div>
                    <div class="col-2">Amount</div>
                    <div class="col-2">Trucks</div>
                </div>
                '''
        meter_amount_sum = 0
        truck_count_sum = 0
        for meter_no in meter_no_list:

            truck_count = len(list([ii.totalizer_start for ii in this_date_input if ii.meter_no == meter_no]))
            truck_count_sum = truck_count_sum + truck_count
            totalizer_start = sorted(list([ii.totalizer_start for ii in this_date_input if ii.meter_no == meter_no]))
            totalizer_end = sorted(list([ii.totalizer_end for ii in this_date_input if ii.meter_no == meter_no]))
            first_totalizer = min(totalizer_start) if totalizer_start else 0
            last_totalizer = max(totalizer_end) if totalizer_end else 0
            meter_amounts = last_totalizer - first_totalizer
            meter_amount_sum = meter_amount_sum + meter_amounts
            data = {'meter_no': int(meter_no),
                               'first_totalizer': first_totalizer,
                               'last_totalizer': last_totalizer,
                               'meter_amounts': meter_amounts,
                               }
            data = f'''
                    <div class="row border-bottom">
                        <div class="col-2 text-center">{meter_no if meter_no != '0' else 'Master'}</div>
                        <div class="col-3">{first_totalizer}</div>
                        <div class="col-3">{last_totalizer}</div>
                        <div class="col-2">{meter_amounts}</div>
                        <div class="col-2">{truck_count}</div>
                    </div>
                    '''
            meter_data = meter_data + data

        totalizer_weighbridge_sum = sum(list([t.totalizer_difference for t in this_date_input if t.weighbridge == 'yes']))
        totalizer_sum = sum(list([t.totalizer_difference for t in this_date_input ]))

        metre_weighbridget_deff = meter_amount_sum + totalizer_weighbridge_sum - totalizer_sum


        total = f'''
                <div class="row border-dark border-bottom border-top">
                    <div class="col-8 text-right">جمع خالص بارگیری شده از میتر</div>
                    <div class="col-2">{meter_amount_sum}</div>
                    <div class="col-2">{truck_count_sum}</div>
                </div>
                <div class="row border-dark border-bottom">
                    <div class="col-8 text-right">جمع خالص میتر در بارگیری از باسکول</div>
                    <div class="col-2">{totalizer_weighbridge_sum}</div>
                </div>
                <div class="row border-dark border-bottom">
                    <div class="col-8 text-right">مقدار اسناد بارگیری توسط میتر و باسکول</div>
                    <div class="col-2">{totalizer_sum}</div>
                </div>
                <div class="row border-dark border-bottom">
                    <div class="col-8 text-right">اختلاف بارگیری میتر و باسکول با اسناد صادر شده</div>
                    <div class="col-2">{metre_weighbridget_deff}</div>
                </div>
                '''
        self.meters = meter_data + total
        mismatch = ''
        # mismatch_record = (meter_no, totalizer_start, totalizer_end, document_no,)
        for meter_no in meter_no_list:
            mismatch_record = sorted(list([[meter_no, rec.totalizer_start, rec.totalizer_end, rec.document_no]
                                           for rec in this_date_input
                                           if rec.meter_no == meter_no]),
                                     key=lambda r: r[1])
            for index in range(len(mismatch_record) - 1):
                if abs(mismatch_record[index][2] - mismatch_record[index + 1][1] ) > 0:
                    r1 = mismatch_record[index]
                    r2 = mismatch_record[index + 1]
                    mismatch = mismatch + f'''
                                        <div class="row border-bottom"> 
                                            <div class="col-3">  {r1[0]} </div>
                                            <div class="col-3">  {r1[1]} </div>
                                            <div class="col-3">  {r1[2]} </div>
                                            <div class="col-3">  {r1[3]} </div>           
                                        </div>
                                        <div class="row border-bottom"> 
                                            <div class="col-3">  {r2[0]} </div>
                                            <div class="col-3">  {r2[1]} </div>
                                            <div class="col-3">  {r2[2]} </div>
                                            <div class="col-3">  {r2[3]} </div>           
                                        </div>
                                        '''
            self.mismatch = ''
            if mismatch != '':
                self.mismatch = f'''
                                    <div class="row mt-4 bg-warning"> 
                                        <div class="col-3">Meter No</div>
                                        <div class="col-3">First Totalizer</div>
                                        <div class="col-3">Last Totalizer</div>
                                        <div class="col-3">Document No</div>           
                                    </div>
                                    {mismatch}
                                    '''
































