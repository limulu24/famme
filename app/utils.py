import re

def validate_input(data):
    """验证输入数据"""
    if not all(data.values()):
        return False
        
    # 验证邮箱格式
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email_pattern.match(data['email']):
        return False
        
    # 验证留言长度
    if len(data['message']) > 1000:
        return False
        
    return True 