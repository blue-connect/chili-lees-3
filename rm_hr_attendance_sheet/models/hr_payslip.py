from odoo import api, fields, models
class HrPayslipInherit(models.Model):

    _inherit = 'hr.payslip'

    def compute_sheet(self):
        summ=0
        late_obj =self.env['late.check_in'].search([('employee_id','=',self.employee_id.id),('date_from','<=',self.date),('date_to','>=',self.date)])
        if late_obj:
            for recc in late_obj:
                summ+=recc.late_minutes
        self.employee_id.latee=summ
        print(summ)

        for payslip in self.filtered(lambda slip: slip.state in ['draft', 'verify']):
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            lines = [(0, 0, line) for line in payslip._get_payslip_lines()]
            payslip.write({'line_ids': lines, 'number': number, 'state': 'verify', 'compute_date': fields.Date.today()})
        return True
