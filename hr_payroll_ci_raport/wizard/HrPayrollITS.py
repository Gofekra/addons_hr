#-*- encoding:utf-8 -*-

from openerp import api, fields, models
from itertools import groupby

class HrPayrollITS(models.TransientModel):
    _name= 'hr.payroll.its'
    _description= "Gestion de l'ITS"

    name= fields.Char('Libellé', required=False)
    lot_id= fields.Many2one('hr.payslip.run', 'Lot de paie', required=True)
    company_id= fields.Many2one('res.company', 'Compagnie', required=True, default=1)

    def computeTotalIGR(self, slips):
        revenu = 0
        total_igr = 0
        total_cn = 0
        res = {}
        line_obj =  self.env['hr.payslip.line']
        for slip in slips :
            part_id= slip.employee_id.part_igr
            cn= line_obj.search([('slip_id', '=', slip.id), ('code', '=', 'CN')]) or False
            its= line_obj.search([('slip_id', '=', slip.id), ('code', '=', 'ITS')]) or False
            brut= line_obj.search([('slip_id', '=', slip.id), ('code', '=', 'BRUT')]) or False
            igr= line_obj.search([('slip_id', '=', slip.id), ('code', '=', 'IGR')]) or False
            print part_id
            print cn
            print its
            if its and cn :
                revenu += ((brut.total * 80/100 - cn.total -its.total) / part_id) * 85 /100
                total_cn+= cn.total
            if igr :
                total_igr+= igr.total

            print revenu
        return {
            'revenu': revenu,
            'igr': total_igr,
            'cn': total_cn
        }


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

    def getAmountBaseIGR(self, slips):
        lines = []
        for slip in slips :
            line= slip.line_ids.filtered(lambda r: r.code == 'IGR')
            print line
            if line :
                lines.append(line)
        print lines
        return lines

    def computedata(self, slips):
        res = {}


    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].get_action(records, 'hr_payroll_ci_raport.hr_payroll_its_report', data=data)



    @api.multi
    def compute(self):
        res = {
            'brut_total': 0,
            'nature': 0,
            'brut': 0,
            'brut_pension': 0,
            'brut_viagiere_1': 0,
            'brut_viagiere_2': 0,
            'revenu_imp_brut': 0,
            'revenu_brut_pension': 0,
            'revenu_brut_viagiere_1': 0,
            'revenu_brut_viagiere_2': 0,
            'model': 'hr.payroll.its'
        }
        self.ensure_one()
        slips= self.lot_id.slip_ids
        res['brut_total']= self.getAmountCode('BRUT')
        res['nature']= self.getAmountCode('RAVTGN')
        res['brut']= res['brut_total'] - res['nature']
        abatements= self.company_id.abatement_ids
        other= self.computeTotalIGR(slips)
        res['revenu']= other['revenu']
        res['igr']= other['igr']
        res['cn']= other['cn']

        print abatements
        total = 0
        lines= self.getAmountBaseIGR(slips)
        for abat in abatements :
            vals= {
                'name': abat.name,
                'code': abat.code,
                'taux': abat.taux,
            }
            if abat.code == 'NORM':
                vals['montant_abatement']= res['brut_total'] * abat.taux/100
                vals['montant']= res['brut_total'] - vals['montant_abatement']
            elif abat.code == 'PEN':
                vals['montant_abatement']= res['brut_pension'] * abat.taux/100
                vals['montant']= res['brut_pension'] - vals['montant_abatement']
            elif abat.code == 'RENT1':
                vals['montant_abatement']= res['brut_viagiere_1'] * abat.taux/100
                vals['montant']= res['brut_viagiere_1'] - vals['montant_abatement']
            else :
                vals['montant_abatement']= res['brut_viagiere_1'] * abat.taux/100
                vals['montant']= res['brut_viagiere_2'] - vals['montant_abatement']
            total+= vals['montant']
            res[abat.code]= vals
        res['total']= total
        res['ids'] = self.id
            # res['abatements'].append(vals)
        print res
        return self._print_report(res)
