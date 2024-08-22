from itsdangerous import URLSafeTimedSerializer as Serializer
from itsdangerous import BadData,BadTimeSignature,BadSignature
from md_mall import settings


def generic_openid(openid):
    s = Serializer(secret_key=settings.SECRET_KEY)
    access_token = s.dumps({'openid': openid})
    return access_token


def check_access_token(token):
    s = Serializer(secret_key=settings.SECRET_KEY)
    try:
        result = s.loads(token,max_age=3600)
    except Exception:
        return None
    else:
        return result.get('openid')