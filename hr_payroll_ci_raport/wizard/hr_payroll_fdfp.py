#-*- coding:utf-8 -*-
__author__ = 'lekaizen'

import time
import babel
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import fields, models, api, _
from itertools import groupby
from openerp.exceptions import UserError


months = [(0, 'Janvier'),(1, 'Février'),(2, 'Mars'),(3, 'Avril'),(4, 'Mai'), (5, 'Juin'), (6, 'Juillet'),(7, 'Aout'),
          (8, 'Septembre'),(9, 'Octobre'),(10, 'Novembre'),(11, 'Décembre')]


class HrPayrollFDFP(models.TransientModel):
    _name = 'hr.payroll.fdfp'
    _description = "Gestion des declarations FDFP"


    name = fields.Char('Nom', required=True, size=155)
    # lot_id = fields.Many2one('h.payslip.run', 'Lot de paie', required=True)
    month = fields.Selection(months, 'Mois', required=False)
    company_id= fields.Many2one('res.company', 'Société', default=1)
    lot_id= fields.Many2one('hr.payslip.run', 'Lot de paie', required=True)

    def getAmountCode(self, code):
        total = 0
        if self.lot_id and code:
            slip_ids = self.env['hr.payslip'].search([('payslip_run_id', 'in', self.lot_id.ids)]).ids
            if slip_ids :
                lines= self.env['hr.payslip.line'].search([('slip_id', 'in', slip_ids), ('code', '=', code)])
                if lines :
                    for line in lines :
                        total+= line.total
        return total

    def computeEffectif(self, slips, date_from, date_to):
        res = []
        categs= self.env['hr.contract.category'].search([])
        employees= self.env['hr.employee'].search([])
        if categs :
            for categ in categs :
                if categ.code == 'S':
                    pass
                else :
                    year_start = date_from+ relativedelta(month=1, day=1)
                    year_end= date_from+ relativedelta(month=12, day=31)
                    bulletins = slips.filtered(lambda r: r.employee_id.category_id.id == categ.id)
                    mensuels_in= employees.filtered(lambda r: r.category_id.id == categ.id and fields.Date.from_string(r.start_date) >= date_from and
                            fields.Date.from_string(r.start_date) <= date_to )
                    mensuels_out= employees.filtered(lambda r: r.category_id.id == categ.id and r.end_date!= False and fields.Date.from_string(r.end_date) >= date_from and
                            fields.Date.from_string(r.end_date) <= date_to )
                    annuel_in= employees.filtered(lambda r: r.category_id.id == categ.id and fields.Date.from_string(r.start_date) >= year_start and
                            fields.Date.from_string(r.start_date) <= year_end )
                    annuel_out= employees.filtered(lambda r: r.category_id.id == categ.id and r.end_date!= False and fields.Date.from_string(r.end_date) >= year_start and
                            fields.Date.from_string(r.end_date) <= year_end )
                    vals = {
                        'categorie': categ.name,
                        'nombre': len(bulletins) or 0,
                        'mens_in': len(mensuels_in) or 0,
                        'mens_out': len(mensuels_out) or 0,
                        'ann_in': len(annuel_in) or 0,
                        'ann_out': len(annuel_out) or 0,
                    }
                    print vals
                    res.append(vals)
        return res



    @api.one
    def check_report(self):
        return True

    def computedata(self, slips, lot_id):
        res = {
            'mensuel': {
                'in': 0,
                'out': 0,
            },
            'annuel': {
                'in': 0,
                'out': 0,
            },
        }
        emp_obj= self.env['hr.employee']
        # emp_ins= slips.filtered(lambda e: e.employee_id.start_date >= lot_id.date_start and e.employee_id.start_date <= lot_id.date_end)
        # print emp_ins
        # year_start=
        start_date = fields.Date.from_string(lot_id.date_start)
        end_date = fields.Date.from_string(lot_id.date_end)
        year_start= end_date + relativedelta.relativedelta(month=1, day=1)
        year_end= end_date + relativedelta.relativedelta(month=12, day=31)
        for slip in slips :
            employee = slip.employee_id
            if employee.start_date and fields.Date.from_string(employee.start_date) <= end_date and \
                            fields.Date.from_string(employee.start_date) >= start_date :
                res['mensuel']['in']+= 1
            if employee.end_date and fields.Date.from_string(employee.end_date) <= end_date and \
                            fields.Date.from_string(employee.end_date) >= start_date :
                res['mensuel']['out']+= 1
            if employee.start_date and fields.Date.from_string(employee.start_date) <= year_end and \
                            fields.Date.from_string(employee.start_date) >= year_start :
                res['annuel']['in']+= 1
            if employee.end_date and fields.Date.from_string(employee.end_date) <= year_end and \
                            fields.Date.from_string(employee.end_date) >= year_start :
                res['annuel']['out']+= 1
            # if start_date and start_date <= date_from and start_date >= date_to :
            #     res['mensuel']['in']+= 1
            # if end_date and end_date <= date_from and end_date >= date_to :
            #     res['mensuel']['out']+= 1
        print res
        return res

    def getCumulBrut(self, slips, code):
        line_obj= self.env['hr.payslip.line']
        amount = 0
        if slips :
            lines= line_obj.search([('slip_id', 'in', slips.ids), ('code', '=', code)])
            print lines
            amount= sum([line.total for line in lines])
        print amount
        return amount


    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].get_action(records, 'hr_payroll_ci_raport.hr_payroll_fdfp_report', data=data)


    @api.multi
    def compute(self):
        res = {
            'effectifs': [],
        }
        self.ensure_one()
        categories = self.env['hr.contract.category'].search([('code', '!=', 'S')], order='name')
        print categories
        slips = self.lot_id.slip_ids
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(self.lot_id.date_start, "%Y-%m-%d")))
        date_start= fields.Date.from_string(self.lot_id.date_start)
        date_end= fields.Date.from_string(self.lot_id.date_end)
        if slips :
            brut= self.getCumulBrut(slips, 'BRUT')
            res['brut']= brut
            print brut
            res['effectifs']= self.computeEffectif(slips, date_start, date_end)
            print res
        res['model']= 'hr.payroll.fdfp'
        res['ids'] = self.id
        return self._print_report(res)

