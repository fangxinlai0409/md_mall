from itsdangerous import URLSafeTimedSerializer as Serializer
from md_mall import settings
def generic_email_verify_token(user_id):
    s = Serializer(secret_key=settings.SECRET_KEY)
    data = s.dumps({'user_id':user_id})
    return data
