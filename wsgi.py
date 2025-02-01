from app import create_app

# 为 gunicorn 提供 application 实例
application = create_app()

if __name__ == "__main__":
    application.run() 