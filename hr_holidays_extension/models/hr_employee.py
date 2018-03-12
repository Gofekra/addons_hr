#-*- coding:utf-8 -*-

from odoo import api, models, fields, _


class Employee(models.Model):

    _inherit = "hr.employee"

    current_leave_state = fields.Selection(compute='_compute_leave_status', string="Current Leave Status",
       selection_add=[('technical','Technical'), ('not_technical','No Technical'), ('chef_service','Chef de service'),
                      ('crh','Chargé des RH'), ('chef_depart','Chef de departement'),('cdaf','RAF'),])