#-*- coding:utf-8 -*-

from openerp import api, fields, models
from itertools import groupby

class HrCnpsMonthly(models.TransientModel):
    _name = 'hr.cnps.monthly'
    _description = "Gestion de la CNPS MENSUEL"


    date_from = fields.Date('Date de début', required=True)
    date_to = fields.Date('Date de fin', required=True)
    company_id= fields.Many2one('res.company', 'Compagnie', required=True, default=1)

    def get_amount_by_code(self, slips, code):
        result = []
        amount = 0
        for slip in slips :
            tmp= slip.line_ids.filtered(lambda r: r.code==code)
            if tmp :
                result+= tmp
        if result :
            amount = sum([line.total for line in result])
        return amount



    def computeBrut(self, type, brut):
        vals = {}
        if type == 'm':
            if brut > 1657315:
                vals['retraite'] = 1657315
                vals['tranche']= 4
            elif brut >= 70000 and brut <= 1657315 :
                vals['retraite']= brut
                vals['tranche']= 3
            else :
                vals['retraite']= brut
                vals['tranche']= 2
            vals['autre_cotisation'] = 70000
        return vals


    def computeValues(self, employee, list_slip):
        # vals = {}
        brut = self.get_amount_by_code(list_slip, 'BRUT')
        print brut
        vals= self.computeBrut(employee.type, brut)

    def compute_data(self, data, tranche):
        vals = {
            'tranche': tranche,
            'nombre': 0,
            'retraite': 0,
            'cotisation': 0
        }
        for item in data:
            if item.get('tranche') == tranche :
                vals['nombre']+= 1
                vals['retraite']+= item.get('retraite')
                vals['cotisation']+= item.get('autre_cotisation')
        return vals

    def get_taux(self, company):
        if company :
            vals= {
                'accident': company.taux_accident_travail,
                'cnps': company.taux_cnps_employee_local+ company.taux_cnps_employer,
                'famille': company.taux_prestation_familiale,
                'maternite': company.taux_assurance_mater
            }
            return vals
        return {}

    def get_totaux(self, data):
        nombre = retraite = cotisation = 0
        for item in data :
            nombre+= item.get('nombre')
            retraite+= item.get('retraite')
            cotisation+= item.get('cotisation')
        return {
            'nombre': nombre,
            'retraite': retraite,
            'cotisation': cotisation
        }


    @api.multi
    def compute(self):
        self.ensure_one()
        res = {}
        res['ids'] = self.id
        res['model'] = 'hr.cnps.monthly'

        data = []
        slip_obj= self.env['hr.payslip']
        slips= slip_obj.search([('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                                ('company_id', '=', self.company_id.id)])
        print slips
        data = []
        results = []
        total_brut = 0
        if slips :
            order = 0

            for employee, list_slip in groupby(slips, lambda l: l.employee_id):
                tmp= list(list_slip)
                brut = self.get_amount_by_code(tmp, 'BRUT')
                total_brut+= brut
                vals= self.computeBrut(employee.type, brut)
                data.append(vals)
            for i in range(5):
                result= self.compute_data(data, i)
                results.append(result)
        res['taux']= self.get_taux(self.company_id)
        res['lines']= results
        res['totaux']= self.get_totaux(results)
        res['retraite']= int(res['totaux']['retraite'] * (res['taux']['cnps']/100))
        res['accident']= int(res['totaux']['cotisation'] * (res['taux']['accident']/100))
        res['famille']= int(res['totaux']['cotisation'] * (res['taux']['famille']/100))
        res['maternity']= int(res['totaux']['cotisation'] * (res['taux']['maternite']/100))
        res['total_brut']= total_brut

        return self._print_report(res)

    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].with_context(landscape=True).get_action(records, 'hr_payroll_ci_raport.cnps_mensuel_report', data=data)