# from rest_framework_simplejwt.authentication import JWTAuthentication


# class CookieJWTAuthentification(JWTAuthentication):
#     def authenticate(self, request):
#         raw_token = request._request.COOKIES.get('access_token')
#         if raw_token is None:
#             return None

#         validated_token = self.get_validated_token(raw_token)
#         return self.get_user(validated_token), validated_token

from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentification(JWTAuthentication):

    def authenticate(self, request):
        raw_token = request.COOKIES.get('access_token')  # ✔ propre

        if not raw_token:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return (user, validated_token)

        except Exception:
            return None
