from flask import Blueprint, render_template, request, flash, current_app, send_file, session
from flask_mail import Message
from app import mail, validate_input, limiter, cache
from app.captcha import generate_captcha, verify_captcha
import time
import secrets

main = Blueprint('main', __name__)

@main.route('/captcha')
@limiter.limit("10 per minute")
def get_captcha():
    """获取验证码"""
    captcha_id, image_io = generate_captcha()
    session['captcha_id'] = captcha_id
    image_io.seek(0)
    return send_file(image_io, mimetype='image/png')

@main.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
@cache.cached(timeout=300, unless=lambda: request.method != 'GET')
def index():
    if request.method == 'POST':
        # CSRF保护
        csrf_token = session.get('csrf_token')
        if not csrf_token or csrf_token != request.form.get('csrf_token'):
            flash('表单已过期，请重试。', 'error')
            return render_template('index.html'), 400

        # 验证码验证
        captcha_id = session.get('captcha_id')
        captcha_input = request.form.get('captcha', '').strip()
        if not verify_captcha(captcha_id, captcha_input):
            flash('验证码错误或已过期。', 'error')
            return render_template('index.html'), 400

        data = {
            'name': request.form.get('name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'message': request.form.get('message', '').strip()
        }
        
        if not validate_input(data):
            flash('请填写所有必填项，并确保格式正确。', 'error')
            return render_template('index.html'), 400
            
        try:
            msg = Message(
                subject=f'新留言来自: {data["name"]}',
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[current_app.config['ADMIN_EMAIL']],
                body=f'''
来自: {data["name"]}
邮箱: {data["email"]}
留言内容:
{data["message"]}
IP: {request.remote_addr}
User-Agent: {request.headers.get('User-Agent')}
时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
'''
            )
            mail.send(msg)
            current_app.logger.info(f'邮件发送成功给 {current_app.config["ADMIN_EMAIL"]}')
            flash('留言已成功发送！', 'success')
        except Exception as e:
            current_app.logger.error(f'发送邮件时出错: {str(e)}')
            flash('发送失败，请稍后重试。', 'error')
            return render_template('index.html'), 500

    # 生成新的CSRF令牌
    session['csrf_token'] = secrets.token_hex(16)
    return render_template('index.html', csrf_token=session['csrf_token'])

@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@main.app_errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

@main.app_errorhandler(429)
def ratelimit_handler(e):
    flash('请求过于频繁，请稍后再试。', 'error')
    return render_template('index.html'), 429 