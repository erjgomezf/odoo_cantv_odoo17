# cantv_theme/__manifest__.py
{
    'name': 'CANTV Theme Customizations',
    'version': '17.0.1.0.0',
    'category': 'Theme/Custom',
    'summary': 'Personalización de branding y colores para Odoo 17 Community.',
    'description': """
        Este módulo aplica un estilo visual adaptado al branding CANTV.
        - Cambia el color del menú superior.
        - Ajusta variables SCSS para el backend.
    """,
    'author': 'Ernesto Gomez',
    'website': 'https://www.cantv.com.ve',
    'license': 'LGPL-3',
    'depends': ['web'],
    'assets': {
        'web.assets_backend': [
            'cantv_theme/static/src/scss/custom_variables.scss',
            'cantv_theme/static/src/scss/custom_styles.scss',
        ],
    },
    'installable': True,
    'application': False,
}
