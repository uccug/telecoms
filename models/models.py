# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, _
from odoo.exceptions import  UserError


SPECTRUM_REQUEST_STATUS_CHOICES = [
    ('draft', 'Draft'), 
    ('submitted', 'Submitted'), 
    ('assessed', 'Assessed'), 
    ('approved', 'Approved'), 
    ('rejected', 'Rejected')
]

LICENSE_APPLICATION_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('submitted', 'submitted'),
]


class Staff(models.Model):
    _name = 'telecoms.staff'
    _description = 'Staff'
    _rec_name = 'staff_name'

    license_application_id = fields.Many2one(
        comodel_name='telecoms.license_application',
        string='Application ID',
        ondelete='cascade',
    )
    staff_name = fields.Char(string='Name')
    job_title = fields.Char(string='Job Title')
    cv_file_name = fields.Char()
    staff_resume_file = fields.Many2one('ir.attachment', string='Resume/CV')


class CompanyDirector(models.Model):
    _name = 'telecoms.company_director'
    _description = 'Company Director'
    _rec_name = 'directors_name'
    
    application_id = fields.Many2one(comodel_name='telecoms.license_application', string='Application ID', ondelete='cascade')

    directors_name = fields.Char(string='Name')
    directors_citizenship = fields.Char(string='Citizenship')
    directors_share_holding = fields.Float(string='Shareholding %')
    directors_id_number = fields.Char(string='ID/Passport Number')
    directors_id_file = fields.Many2one('ir.attachment', string='ID')


class LicenseApplication(models.Model):
    _name = 'telecoms.license_application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'License Application'

    def _get_user_id(self):
        user = self.env['res.users'].search([('id', '=', self.env.uid)], limit=1)
        return user.id
        
    name = fields.Char(required=True, default=lambda self: _('New'), copy=False)
    state = fields.Selection(LICENSE_APPLICATION_STATUS_CHOICES, string='Status', default='draft')

    application_type = fields.Selection([('new', 'New'), ('renewal', 'Renewal'), ('transfer','Transfer')], default='new')
    license_type = fields.Selection([
        ("NTO", "National Telecommunications Operator"),
        ("NPIP", "National Public Infrastructure Provider"),
        ("NPSP", "National Public Service Provider"),
        ("RPIP", "Regional Public Infrastructure Provider"),
        ("RPSP", "Regional Public Service Provider")
    ])

    company_name = fields.Char(string='Company Name')
    company_email = fields.Char(string='Company Email')
    company_tel = fields.Char(string='Company Tel')
    company_postal_address = fields.Char(string='Company Postal Address')
    company_physical_address = fields.Char(string='Company Physical Address')
    company_tin = fields.Char(string='Tax Identification Number')

    contact_person_name = fields.Char(string='Contact Person Name')
    contact_person_address = fields.Char(string='Contact Person Address')
    contact_person_email = fields.Char(string='Contact Person Email')
    contact_person_number = fields.Char(string='Contact Person Tel')


    certificate_of_incorporation = fields.Many2one('ir.attachment', string='Certificate of Incorporation')
    mem_arts = fields.Many2one('ir.attachment', string='Memorand and Articles of Association')
    tax_clearance_certificate = fields.Many2one('ir.attachment', string='Tax Clearance Certificate')
    organization_chart = fields.Many2one('ir.attachment', string='Organization Chart')


    company_directors = fields.One2many(
        string="Company Directors",
        comodel_name='telecoms.company_director',
        inverse_name='application_id'
    )

    organization_chart = fields.Many2one('ir.attachment', string='Organization Chart')
    key_management_staff = fields.One2many(
        string="Key Management Staff",
        comodel_name='telecoms.staff',
        inverse_name='license_application_id'
    )

    executive_summary = fields.Many2one('ir.attachment', string='Executive Summary')
    financial_statements = fields.Many2one('ir.attachment', string='Financial Statements')
    source_of_funding = fields.Many2one('ir.attachment', string='Source of Funding')
    revenue_projections = fields.Many2one('ir.attachment', string='Revenue Projections')

    submission_date = fields.Datetime(string='Submission Date')
    applicant = fields.Many2one('res.users', string="Applicant", default=_get_user_id, help='Name of Applicant')

    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")


    @api.multi
    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'telecoms.license_application'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)