import base64
import datetime
import logging
import werkzeug
import pprint
import os

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError
from odoo.addons.web.controllers.main import content_disposition



_logger = logging.getLogger(__name__)


class TelecomsPortalController(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(TelecomsPortalController, self)._prepare_portal_layout_values()
        values['telecom_license_applications_count'] = request.env['telecoms.license_application'].sudo().search_count([('applicant', '=', request.env.user.id)])
        return values

    @http.route(['/my/telecom/licenses', '/my/telecom/licenses/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_telecom_licenses(self, page=0, sortby=None, **kw):
        values = self._prepare_portal_layout_values()

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        applications = request.env['telecoms.license_application'].sudo().search(
            [('applicant', '=', request.env.user.id)],
            order=order
        )
        total = applications.search_count([])
        pager = request.website.pager(
            url='/my/telecom/licenses',
            total=total,
            page=page,
            step=10,
        )
        offset = pager['offset']
        applications = applications[offset: offset + 10]
        values.update({
            'applications': applications,
            'page_name': 'license_application',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("telecoms.portal_telecom_licenses_list", values)

    @http.route(['/my/telecom/authorizations', '/my/telecom/authorizations/<int:page>'], type='http', auth="user", website=True)
    def portal_my_telecom_authorizations(self, page=0, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        return request.render("telecoms.portal_telecom_authorizations_list", values)


    @http.route(['/telecoms/licenses/apply'], type='http', auth="user", website=True)
    def create_telcom_license_application(self, **kwargs):
        values = self._prepare_portal_layout_values()

        if request.httprequest.method == 'POST':
            action = kwargs.get('action', False)
            params = kwargs
            params['applicant'] = request.env.user.id

            record = request.env['telecoms.license_application'].sudo()
            application = record.create({'company_name': kwargs['company_name'], 'applicant': request.env.user.id})
            application_id = application.id


            # self.process_application(application_id=application.id, kwargs=kwargs, step=1)

            directors_names = request.httprequest.form.getlist('directors_name')
            citizenships = request.httprequest.form.getlist('directors_citizenship')
            share_holdings = request.httprequest.form.getlist('directors_share_holding')
            id_numbers = request.httprequest.form.getlist('directors_id_number')
            id_files = request.httprequest.files.getlist('directors_id_file')


            company_directors = [(0, 0, {
                'directors_name': directors_name,
                'directors_citizenship': citizenship,
                'directors_share_holding': share_holding,
                'directors_id_number': id_number,
                'directors_id_file': request.env['ir.attachment'].sudo().create({
                    'name': "%s's ID" % directors_name,
                    'datas_fname': "%s's ID" % directors_name,
                    'type': 'binary',
                    'datas': base64.encodestring(id_file.read()),
                    'res_model': 'broadcasting.license_application',
                    'res_id': application_id,
                })
            }) for directors_name, citizenship, share_holding, id_number, id_file in zip(directors_names, citizenships, share_holdings, id_numbers, id_files) if directors_name.strip() != ""]
                            
            kwargs['company_directors'] = company_directors
            for key in ['directors_name', 'directors_citizenship', 'directors_share_holding', 'directors_id_number', 'directors_id_file']:
                if key in kwargs:
                    del kwargs[key]


            staff_names = request.httprequest.form.getlist('staff_name')
            staff_titles = request.httprequest.form.getlist('staff_job_title')
            staff_cvs = request.httprequest.files.getlist('staff_cv_file')


            key_staff = [(0, 0, {
                'staff_name': staff_name,
                'job_title': staff_title,
                'cv_file_name': cv.filename,
                'staff_resume_file': request.env['ir.attachment'].sudo().create({
                    'name': "%s's CV" % staff_name,
                    'datas_fname': "%s's CV" % staff_name,
                    'type': 'binary',
                    'datas': base64.encodestring(cv.read()),
                    'res_model': 'broadcasting.license_application',
                    'res_id': application_id,
                })
            }) for staff_name, staff_title, cv in zip(staff_names, staff_titles, staff_cvs) if staff_name.strip() != ""]
     
            kwargs['key_management_staff'] = key_staff

            for key in ['staff_name', 'staff_job_title', 'staff_cv_file']:
                if key in kwargs:
                    del kwargs[key]

            attachment_fields = [
                {'name':'certificate_of_incorporation','description': 'Certificate of Incorporation'},
                {'name':'mem_arts', 'description': 'Memorand and Articles of Association'},
                {'name':'tax_clearance_certificate', 'description': 'Tax Clearance Certificate'},
                {'name':'executive_summary', 'description': 'Executive Summary'},
                {'name':'financial_statements', 'description': 'Financial Statements'},
                {'name':'source_of_funding', 'description': 'Source of Funding'},
                {'name':'revenue_projections', 'description': 'Revenue Projections'},
            ]

            for attachment_field in attachment_fields:
                if kwargs.get(attachment_field['name'], False):
                    field_name = attachment_field['name']
                    file = kwargs[attachment_field['name']]
                    name = file.filename
                    filename, file_extension = os.path.splitext(file.filename)

                        
                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': attachment_field['description'], 
                        'type': 'binary',
                        'datas': base64.encodestring(file.read()),
                        'datas_fname': "%s%s" % (attachment_field['description'], file_extension),
                        'res_model': 'broadcasting.license_application',
                        'res_id': application_id,
                        'create_uid': request.env.user.id
                    })

                    fields_metadata = application.fields_get([field_name])
                    current_attachment = application[field_name]

                    if current_attachment:
                        application[field_name] = False
                        current_attachment.sudo().unlink()

                    kwargs[attachment_field['name']] = attachment.id
                else:
                    del kwargs[attachment_field['name']]


            if kwargs.get('next', False):
                del kwargs['next']

            if kwargs.get('action', False):
                del kwargs['action']

            application.update(kwargs)

            if action == 'save':
                return werkzeug.utils.redirect('/my/telecoms/licenses/')
            
        return request.render("telecoms.portal_telecom_license_application_form", values)

    def update_license_application(self):
        pass

    
    def list_authorisations(self):
        pass

    def create_authorisation(self):
        pass
    