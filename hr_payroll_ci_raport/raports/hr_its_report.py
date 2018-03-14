# -*- coding: utf-8 -*-

from datetime import datetime
import time
from odoo import api, models, fields
from odoo.addons_tools import format_amount

from itertools import groupby


class ReportHrPayrollFDFP(models.AbstractModel):
    _name = 'report.hr_payroll_ci_raport.hr_payroll_its_report'

    # def get_total_efectif(self, data):
    #     res = {
    #         'total_emp': 0,
    #         'total_mens_in': 0,
    #         'total_mens_out': 0,
    #         'total_an_in': 0,
    #         'total_an_out': 0
    #     }
    #     for dt in data :
    #         res['total_emp']+= dt['nombre']
    #         res['total_mens_in']+= dt['mens_in']
    #         res['total_mens_out']+= dt['mens_out']
    #         res['total_an_in']+= dt['ann_in']
    #         res['total_an_out']+= dt['ann_out']
    #     print res
    #     return res
    #
    def get_element(self, docs):
        if docs.lot_id :
            date_start = fields.Date.from_string(docs.lot_id.date_start)
            print date_start.month
            res = {
                'month_1': 0,
                'month_2': 0,
                'trim': 0,
                'year_1': str(date_start.year)[2],
                'year_2': str(date_start.year)[3],
                'quarter': (date_start.month)//3
            }
            print date_start.month
            if len(str(date_start.month)) <2 :
                res['month_1']= 0
                res['month_2']= str(date_start.month)[0]
            else :
                res['month_1']= str(date_start.month)[0]
                res['month_2']= str(date_start.month)[1]
        print res
        # print docs
        return res

    @api.model
    def render_html(self, docids, data=None):
        self.model = data['model']
        docs = self.env[self.model].browse(data['ids'])
        # print data['form']
        # results = self._lines(data['form']['date_from'], data['form']['date_to'], data['form']['company_id'][0])
        # lines = results['lines']
        # codes = results['codes']
        # headers = results['headers']
        lang_code = 'fr_FR'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        # total_effectif= self.get_total_efectif(data['effectifs'])
        # # print total_effectif
        # data['total_effectifs']= total_effectif
        result = self.get_element(docs)
        data.update(result)
        # print data
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data,
            'docs': docs,
            'time': time,
            'format_amount': format_amount.manageSeparator,
        }
        return self.env['report'].render('hr_payroll_ci_raport.hr_payroll_its_report', docargs)
