#-*- coding:utf-8 -*-

from openerp import api, fields, models
from itertools import groupby

class HrPayrollDISA(models.TransientModel):
    _name= 'hr.payroll.disa'
    _description= "Gestion de la DISA"

    date_from= fields.Date("Date de début", required=True)
    date_to= fields.Date("Date de fin", required=True)
    company_id= fields.Many2one('res.company', 'Société', default=1, required=True)

    def get_number_worked_hour(self, slips):
        result = []
        number = 0.0
        for slip in slips :
            tmp= slip.worked_days_line_ids.filtered(lambda r: r.code == 'WORK100' or r.code == 'CONG')
            if tmp :
                result+= tmp
        if result :
            print result
            number = sum([line.number_of_days for line in result])
        return number


    def get_amount_by_code(self, slips, code, type=None):
        result = []
        amount = 0
        for slip in slips :
            tmp= slip.line_ids.filtered(lambda r: r.code==code)
            if tmp :
                result+= tmp
        if result :
            print result
            if type is None :
                amount = sum([line.total for line in result])
            else :
                print 'on est ici'
                amount = sum([line.amount for line in result])
        return amount

    @api.one
    def compute(self):
        slip_obj= self.env['hr.payslip']
        slips= slip_obj.search([('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to)])
        print slips
        data = []
        if slips :
            order = 0
            for employee, list_slip in groupby(slips, lambda l: l.employee_id):
                print list_slip
                order+= 1
                print type(employee.birthday)
                tmp = list(list_slip)
                val = {
                    'num': order,
                    'name': employee.name,
                    'cnps': employee.matricule_cnps,
                    'year': employee.birthday[:4],
                    'brut': self.get_amount_by_code(tmp, 'BRUT'),
                    'retraite': self.get_amount_by_code(tmp, 'CNPS', type='pfd'),
                    'cotisation': self.get_amount_by_code(tmp, 'PF', type='pfd'),
                    'in': employee.start_date,
                    'out': employee.end_date,
                    'type': str(employee.type).upper(),
                    'number_hour': self.get_number_worked_hour(tmp),
                }
                data.append(val)
        return data
        # print data

    def _print_report(self, data):

        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].with_context(landscape=True).get_action(records, 'hr_payroll_ci_raport.report_payroll', data=data)

    @api.multi
    def check_report(self):
        self.ensure_one()
        print self.id
        data = {}
        data['ids'] = self.id
        data['model'] = 'hr.payroll.disa'
        data['form'] = self.read(['date_from', 'date_to', 'company_id'])[0]
        data['lines']= self.compute()
        print data
        return self._print_report(data)