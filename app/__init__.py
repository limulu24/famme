from flask import Flask, render_template, request, flash, current_app
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import logging
from logging.handlers import RotatingFileHandler
import os
import re

# 初始化扩展
mail = Mail()
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["30 per minute"],
    storage_uri="memory://"
)

def validate_input(data):
    """验证输入数据"""
    if not all(data.values()):
        return False
    if len(data['message']) > 1000:
        return False
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
        return False
    return True

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # 初始化扩展
    mail.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # 配置日志
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/famme.log', 
        maxBytes=10240, 
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    # 安全中间件
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    # 注册路由
    from app.routes import main
    app.register_blueprint(main)

    return app 