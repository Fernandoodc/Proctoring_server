"""from decouple import config

import datetime
import jwt
import pytz
import traceback

# Logger
from src.utils.Logger import Logger


class Security():

    secret = config('JWT_KEY')
    tz = pytz.timezone("America/Lima")

    @classmethod
    def generate_token(cls, authenticated_user):
        try:
            payload = {
                'iat': datetime.datetime.now(tz=cls.tz),
                'exp': datetime.datetime.now(tz=cls.tz) + datetime.timedelta(minutes=10),
                'username': authenticated_user.username,
                'fullname': authenticated_user.fullname,
                'roles': ['Administrator', 'Editor']
            }
            return jwt.encode(payload, cls.secret, algorithm="HS256")
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())

    @classmethod
    def verify_token(cls, cookies, requiredRol):
        try:
            if 'access-token' in cookies.keys():
                authorization = cookies.get('access-token')
                encoded_token = authorization.split(" ")[0]
                if ((len(encoded_token) > 0)):
                    try:
                        payload = jwt.decode(encoded_token, cls.secret, algorithms=["HS256"])
                        roles = list(payload['roles'])
                        print(roles)
                        if requiredRol in roles:
                            return True
                        return False
                    except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError):
                        return False

            return False
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
"""