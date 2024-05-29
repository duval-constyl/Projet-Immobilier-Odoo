# -*- coding: utf-8 -*-
{
    'name': "Wisdom International",  # Module title
    'summary': "Planifiez les descentes et l'achat des terrains",  # Module subtitle phrase
    'description': """
        Gestion WISDOM INTERNATIONAL
        ==============
        Description relies à l'achat et planification descente sur le terrain.
    """,  # Supports reStructuredText(RST) format
    'author': "FOTS FOALENG Duval",
    'website': "http://www.example.com",
    'category': 'Tools',
    'version': '1.0',
    'depends': ['base','mail','account','board'],
    # This data files will be loaded at the installation (commented because file is not added in this example)
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        # 'data/mail_template.xml',
        'views/wisdom_client_views.xml',
        'views/wisdom_employes_views.xml',
        'views/wisdom_achat_views.xml',
        'views/wisdom_dashboard_views.xml',
        # 'views/wisdom_planification_views.xml',
        'views/wisdom_planification_emp_views.xml',
        'report/report.xml',
        'report/wisdom_achat_report_templates.xml',
        'report/wisdom_planification_report_templates.xml',
    ],
    # This demo data files will be loaded if db initialize with demo data (commented because file is not added in this example)
    'demo': [
        'demo/wisdom_client_demo.xml',
        'demo/wisdom_employe_demo.xml',
    ],
    'installable': True,
    'images': "icon.png",
    'application': True,
    'license': "LGPL-3",
    'sequence': -100
}
