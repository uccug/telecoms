{
    'name': 'Telecommunications',
    'version': '1.0',
    'summary': 'Telecommunications',
    'description': "Telecommunications",
    'website': 'https://eservices.ucc.co.ug',
    'depends': [
        'fetchmail',
        'document',
        'web_tour',
        'digest',
        'website',
        'website_partner', 
        'website_mail', 
        'website_form',
        'portal',
    ],
    'data': [
        'security/usergroups.xml',
        'security/ir.model.access.csv',
        # 'data/application_stages.xml',
        # 'data/sequences.xml',
        # 'wizards/create_assessment_report.xml',
        # 'wizards/create_review.xml',
        # 'wizards/create_billing_advise.xml',
        # 'wizards/assessment_report_recommendation.xml',
        # 'wizards/create_rejection.xml',
        'wizards/legal/views.xml',
        'views/internal.xml',
        'views/assessments/legal.xml',
        'templates/portal.xml',
        'templates/email.xml',

    ],
    'demo': [

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
