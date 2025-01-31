import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # 基础配置
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # 安全配置
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = 1800  # session过期时间30分钟
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # CSRF保护
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.urandom(32)
    
    # 邮件配置
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
    
    # 限流配置
    RATELIMIT_DEFAULT = "30/minute"
    RATELIMIT_STORAGE_URL = "memory://"

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # 生产环境特定配置
    SERVER_NAME = 'your-domain.com'  # 替换为您的域名
    PREFERRED_URL_SCHEME = 'https' 