#-*- coding:utf-8 -*-

from openerp import api, fields, models
import time
from datetime import datetime
from itertools import groupby

class HrPayrollReport(models.TransientModel):
    _name= 'hr.payroll.report'
    _description= "Gestion des Etats de virement de salaire"

    type= fields.Selection([('date', 'Par date'), ('lot', 'Par lot depaie')], 'Type de génération', required=True,
               default='lot')
    lot_id= fields.Many2one('hr.payslip.run', 'Lot de paie', required=True)
    date_start= fields.Date("Début")
    date_end= fields.Date('Fin')

    def get_amount_by_code(self, slips, code):
        result = []
        amount = 0
        for slip in slips :
            tmp= slip.line_ids.filtered(lambda r: r.code==code)
            print tmp
            employee= slip.employee_id
            value= {
                'contract': slip.contract_id.type_id.name,
                'matricule': employee.identification_id,
                'name': employee.name,
                'bank': employee.bank_account_id.bank_id.name,
                'code_bank': employee.bank_account_id.bank_id.bic,
                'code_guichet': employee.bank_account_id.code_guichet,
                'num_account': employee.bank_account_id.acc_number,
                'rib': employee.bank_account_id.rib,
                'net': tmp.total
            }
            result.append(value)
        return result

    def get_employee_by_type(self, slips):
        res = {
            'stagiaires': [],
            'employees': []
        }
        stagiaires= slips.filtered(lambda r: r.employee_id.category_id.code == 'S')
        if stagiaires :
            res['stagiaires']= stagiaires
        employees= slips.filtered(lambda r: r.employee_id.category_id.code != 'S')
        if employees :
            res['employees']= employees
        return res

    def computeData(self, slips, category):
        res = []
        if slips :
            if category == 'employees':
                for bank, list_slip in groupby(slips, lambda l: l.employee_id.bank_account_id.bank_id ):
                    payslips= list(list_slip)
                    result= self.get_amount_by_code(payslips, 'NET')
                    vals = {
                        'bank': bank.name,
                        'liste': result
                    }
                    res.append(vals)
            else :
                for employee, list_slip in groupby(slips, lambda l: l.employee_id ):
                    payslips= list(list_slip)
                    result= self.get_amount_by_code(payslips, 'NET')
                    print result
                    print employee.name
                    if result :
                        res.append(result[0])
        return res

    def _print_report(self, data):
        print data
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].get_action(records, 'hr_payroll_ci_raport.hr_payroll_etat_report', data=data)


    @api.multi
    def compute(self):
        self.ensure_one()
        res = {
            'ids': self.id,
            'model': 'hr.payroll.report',
            'employees': [],
            'stagiaires': []
        }
        slips = False
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(self.lot_id.date_start, "%Y-%m-%d")))
        if self.type == 'lot':
            slips = self.lot_id.slip_ids
            print slips
            res['period']= ttyme.strftime('%B-%Y')
        category= self.get_employee_by_type(slips)
        print category
        if category['employees'] :
            ids = [r.employee_id.id for r in category['employees']]
            print ids
            emp_slips= slips.filtered(lambda r: r.employee_id.id in ids)
            print emp_slips
            data= self.computeData(emp_slips, 'employees')
            res['employees']= data
            print data
        if category['stagiaires']:
            stag_slips= slips.filtered(lambda r:r.employee_id.id in category['stagiaires'].ids)
            data= self.computeData(stag_slips, 'stagiaires')
            print data
            res['stagiaires']= data
        print self._context

        return self._print_report(res)

        # print emp_slips
