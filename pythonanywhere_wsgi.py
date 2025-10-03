"""
PythonAnywhere WSGI Configuration Template
Bu dosyayı /var/www/nurhaksekerci_pythonanywhere_com_wsgi.py olarak kopyalayın

NOT: 'nurhaksekerci' yerine kendi kullanıcı adınızı yazın
"""

import os
import sys

# Add your project directory to the sys.path
path = '/home/nurhaksekerci/baskentpsikoloji'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Import Django
from django.core.wsgi import get_wsgi_application

# Initialize Django
application = get_wsgi_application()

# Debug information (remove in production)
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Python version: {sys.version}")
logger.info(f"Python path: {sys.path}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Project path: {path}")
logger.info("Django WSGI application loaded successfully")

# Test imports (remove in production)
try:
    from school.models import Student
    logger.info("School models imported successfully")
except Exception as e:
    logger.error(f"Failed to import school models: {e}")

try:
    from django.conf import settings
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Allowed hosts: {settings.ALLOWED_HOSTS}")
except Exception as e:
    logger.error(f"Failed to load settings: {e}")