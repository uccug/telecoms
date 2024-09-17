import datetime
from odoo import models, fields


class LegalAssessmentReview(models.TransientModel):
    _name="telecoms.legal_assessment.review"
    _description='Legal Assessment Review'

    def _get_current_user_id(self):
        return self.env.uid	

    assessment_id = fields.Many2one('telecoms.legal_assessment', string='Legal Assessment')
    review_comments = fields.Text()


    def submit(self):
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for rec in self:
            rec.assessment_id.update({
                'state': 'reviewed',
                'reviewed': True,
                'review_comments': self.review_comments, 
                'reviewed_by': employee.id,
                'reviewed_at': datetime.datetime.now()
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    

class LegalAssessmentRejection(models.TransientModel):
    _name = "telecoms.legal_assessment.rejection"
    _description = 'Legal Assessment Rejection'

    def _get_current_user_id(self):
        return self.env.uid	

    assessment_id = fields.Many2one('telecoms.legal_assessment', string='Legal Assessment')
    rejection_comments = fields.Text()


    def submit(self):
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        self.assessment_id.update({
            'state': 'rejected',
            'rejected': True, 
            'rejected_by': employee.id,
            'rejected_at': datetime.datetime.now(),
            'rejection_comments': self.rejection_comments
        })
        self.assessment_id.spectrum_request_id.update({'state': 'rejected'})

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }