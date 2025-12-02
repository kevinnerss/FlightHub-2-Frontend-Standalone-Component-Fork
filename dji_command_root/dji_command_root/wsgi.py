"""
ASGI config for dji_command_root project.
"""

import os

from django.core.wsgi import get_wsgi_application

# 【核心修改点】将 dji_command_center 修正为 dji_command_root
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dji_command_root.settings")

application = get_wsgi_application()