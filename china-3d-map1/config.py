SQLALCHEMY_BINDS = {
    'default': 'mysql+pymysql://root:123456@localhost:3306/shixun',
    'zhaoping': 'mysql+pymysql://root:123456@localhost:3306/zhaoping'
}
SQLALCHEMY_DATABASE_URI = SQLALCHEMY_BINDS['default']
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'your-secret-key' 