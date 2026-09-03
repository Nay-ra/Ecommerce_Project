from django.apps import AppConfig

class UserAuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'User_Authentication'

    def ready(self):
        # Import models and signals inside ready() after app registry is loaded
        from django.contrib.auth.signals import user_logged_in
        from Shopping_Cart.utils import merge_session_cart_to_user

        def on_user_logged_in(sender, request, user, **kwargs):
            session_cart_id = request.session.get('cart_id')
            if session_cart_id:
                merge_session_cart_to_user(user, session_cart_id)
                request.session.pop('cart_id', None)

        user_logged_in.connect(on_user_logged_in)