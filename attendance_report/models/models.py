# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
from datetime import date, timedelta


class attendance_report(models.Model):

    _inherit = 'hr.attendance'

    checkin_date = fields.Date("check in date" ,compute="_compute_date",store=True)
    checkout_date = fields.Date("check in date" ,compute="_compute_date",store=True)

    @api.depends('check_in','check_out')
    def _compute_date(self):
        for rec in self:
            if rec.check_in:
                print(rec.check_in.date())
                rec.checkin_date = rec.check_in.date()
            else:
                rec.checkin_date=False
        for rec1 in self:
            if rec1.check_out:
                print(rec.check_out.date())
                rec1.checkout_date = rec1.check_out.date()
            else:
                rec1.checkout_date=False

class AttendanceReport(models.TransientModel):
    _name = 'attendance.report'
    _description = "Attendance Report Wizard"

    from_date = fields.Date('From Date', default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
                            required=True)
    to_date = fields.Date("To Date", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True)
    employee_id = fields.Many2many('hr.employee', string="Employee")


    def print_report(self):
        domain = []
        datas = []
        if self.employee_id:
            domain.append(('id', '=', self.employee_id.ids))

        employees = self.env['hr.employee'].search(domain)
        for employee in employees:
            present = 0
            absent = 0
            tz = timezone(employee.resource_calendar_id.tz)
            date_from = tz.localize(datetime.combine(fields.Datetime.from_string(str(self.from_date)), time.min))
            date_to = tz.localize(datetime.combine(fields.Datetime.from_string(str(self.to_date)), time.max))

            intervals = employee.list_work_time_per_day(date_from, date_to, calendar=employee.resource_calendar_id)
            print(intervals)
            print('-----------------------')
            delta = date_to-date_from
            flag =False
            for i in range(delta.days + 1):

                day = date_from + timedelta(days=i)
                # print(day.date())
                attendances = self.env["hr.attendance"].search(
                    [('employee_id', '=', employee.id), ('checkin_date', '=', day.date())
                     ])
                for att in attendances:
                    if att.check_out:
                        flag=True

                if attendances:
                    print(attendances)
                    print(day)
            # for rec in intervals:
            #     print(rec[0])
            #     attendances = self.env["hr.attendance"].search(
            #         [('employee_id', '=', employee.id), ('check_in', '>=', rec[0]),
            #          ('check_in', '<=', rec[0])])
                print(attendances)
                if attendances and flag:
                    present += 1
                else:
                    absent += 1

            datas.append({
                    'id': employee.id,
                    'name':employee.name,
                    'present': present,
                    'absent': absent,
                })
            flag=False
        res = {
            'attendances':datas,
            'start_date': self.from_date,
            'end_date': self.to_date,
        }
        data = {
            'form': res,
        }
        return self.env.ref('attendance_report.report_hr_attendance').report_action([],data=data)
