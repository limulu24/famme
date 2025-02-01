from io import BytesIO
from captcha.image import ImageCaptcha
import random
import string
from app import cache

def generate_captcha():
    """生成验证码"""
    # 生成随机字符串
    chars = string.ascii_letters + string.digits
    code = ''.join(random.choice(chars) for _ in range(4))
    
    # 生成图片
    image = ImageCaptcha(width=160, height=60)
    image_data = image.generate(code)
    
    # 生成唯一标识
    captcha_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    # 存储到缓存
    cache.set(f'captcha_{captcha_id}', code.lower(), timeout=300)  # 5分钟过期
    
    return captcha_id, BytesIO(image_data.getvalue())

def verify_captcha(captcha_id, user_input):
    """验证验证码"""
    if not captcha_id or not user_input:
        return False
    
    # 获取并删除缓存的验证码
    correct_code = cache.get(f'captcha_{captcha_id}')
    if correct_code:
        cache.delete(f'captcha_{captcha_id}')
        return user_input.lower() == correct_code
    
    return False 