# -*- coding: utf-8 -*-

from datetime import datetime
import time
from odoo import api, models
from odoo.addons_tools import  format_amount

from itertools import groupby


class ReportHrPayrollDisa(models.AbstractModel):
    _name = 'report.hr_payroll_ci_raport.disa_report'


    _codes_rules = []

    def _lines(self, data):
        res = {}


    def _lines_total(self, codes, lines):
        res = {}
        for code in codes :
            total = 0
            for line in lines :
                if line[code] is not None :
                    total+= line[code]
            res[code] = total
        return res

    @api.model
    def render_html(self, docids, data=None):
        self.model = data['model']
        docs = self.env[self.model].browse(data['ids'])
        print data['form']
        results = self._lines(data['form']['date_from'], data['form']['date_to'], data['form']['company_id'][0])
        lines = results['lines']
        codes = results['codes']
        headers = results['headers']
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        date_from = datetime.strptime(data['form']['date_from'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        date_to = datetime.strptime(data['form']['date_to'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        total = self._lines_total(codes, lines)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
            'lines': lines,
            'lines_total': total,
            'codes': codes,
            'headers': headers,
            'time': time,
            'format_amount': format_amount,
        }
        return self.env['report'].render('hr_payroll_ci_raport.report_payroll', docargs)
