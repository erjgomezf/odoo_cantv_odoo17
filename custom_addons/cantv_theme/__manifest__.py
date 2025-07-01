# cantv_theme/__manifest__.py
{
    'name': 'CANTV Theme Customizations',
    'version': '17.0.1.0.0',
    'category': 'Theme/Custom',
    'summary': 'Personalización de branding y colores para Odoo 17 Community.',
    'description': """
        Este módulo aplica un estilo visual adaptado al branding CANTV.
        - Cambia el color principal del menú.
        - Actualiza variables SCSS para el backend.
        - Permite extender plantillas visuales si es necesario.
    """,
    'author': 'Ernesto Gomez',
    'website': 'https://www.cantv.com.ve',
    'license': 'LGPL-3',
    'depends': ['web'],
    'data': [
        'views/assets.xml',
    ],
    'installable': True,
    'application': False,
}
