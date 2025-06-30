{
    'name': 'CANTV Theme Customizations',
    'version': '17.0.1.0.0',
    'category': 'Theme/Custom',
    'summary': 'Customizations for CANTV branding in Odoo 17 Community.',
    'description': """
        This module applies custom styling for CANTV branding.
        - Changes primary color to CANTV blue.
        - Updates company logo.
    """,
    'author': 'Ernesto Gomez',
    'website': 'https://www.cantv.com.ve',
    'depends': ['web', 'base'], # Depende del módulo web para las assets
    'data': [
        'views/custom_web_templates.xml',
        'views/assets.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}