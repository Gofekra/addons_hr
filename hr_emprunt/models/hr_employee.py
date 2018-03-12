#-*- coding:utf-8 -*-


from odoo import api, fields, models, _

class HrEmployee(models.Model):
    _inherit= 'hr.employee'


    loaning_ids= fields.One2many('hr.emprunt.loaning', 'employee_id', 'Écheanciers')
    demande_ids= fields.One2many('hr.emprunt.demande', 'employe_id', 'Demandes')


    @api.one
    def get_amount_emprunt(self, employee_id, date_start, date_end):
        loaning_obj= self.env['hr.emprunt.loaning']
        amount = 0
        print "ok cool pourle test"
        print amount
        print employee_id
        if employee_id :
            # echanes= []
            loanings= loaning_obj.search([('employee_id', '=', employee_id)])
            print loanings
            if loanings :
                for loaning in loanings :
                    print loaning.echeance_ids
                    echeances = loaning.echeance_ids.filtered(lambda r: r.date_prevu <= date_end and r.date_prevu >= date_start)
                    print '************************************************'
                    print echeances
                    if echeances :
                        amount= sum([ech.montant for ech in echeances])
        print "mount total is %s" %amount
        return amount