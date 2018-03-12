# -*- coding: utf-8 -*-

from datetime import datetime
import time
from openerp import api, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, format_amount

from itertools import groupby


class ReportHrPayrollReport(models.AbstractModel):
    _name = 'report.hr_payroll_ci_raport.hr_payroll_etat_report'

    def get_total(self, data):
        amount = 0
        for line in data['liste']:
            amount+= line['net']
            print amount
        return amount

    def get_total_stagiaire(self, data):
        amount= sum([dt['net'] for dt in data])
        return amount

    def get_total_global(self, data):
        amount = 0
        for dt in data['employees']:
            tmp= sum([line['net'] for line in dt['liste']])
            print tmp
            amount+= tmp
        return amount


    # def compute_all(self, data, tranche, code):
    #     for item in data :
    #         if item.get('tranche') == tranche:
    #             result = item.get(code)
    #             if result == 0 :
    #                 return ''
    #             else :
    #                 return result
    #     return ''
    #
    # def compute_total(self, data):
    #     amount = data['retraite'] + data['accident'] + data['famille'] + data['maternity']
    #     return int(amount)

    @api.model
    def render_html(self, docids, data=None):
        self.model = data['model']
        docs = self.env[self.model].browse(data['ids'])
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data,
            'docs': docs,
            'time': time,
            'get_total': self.get_total,
            'get_total_global': self.get_total_global,
            'get_total_stagiaire': self.get_total_stagiaire,
            # 'compute_total': self.compute_total,
            'format_amount': format_amount.manageSeparator,
        }
        return self.env['report'].render('hr_payroll_ci_raport.hr_payroll_etat_report', docargs)
