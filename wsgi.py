import sys
import os

# 애플리케이션 경로 추가
sys.path.insert(0, '/var/www/app2')

from app import create_app
application = create_app()