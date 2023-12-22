from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import get_adapter as get_account_adaptor
import logging

class CustomSocialAccountAdaptor(DefaultSocialAccountAdapter):
    
    def save_user(self, request, sociallogin, form=None):
        u = sociallogin.user
        u.set_unusable_password()

        get_account_adaptor().populate_username(request, u)
        sociallogin.save(request)
        return u
    
    def populate_user(self, request, sociallogin, data):
        print(data)
        first_name = data.get("first_name") or ''
        last_name = data.get("last_name") or ''
        bits_id = data.get('email')[:9] or ''
        
        print(first_name.upper())
        print(last_name.lower())
        
        user = sociallogin.user
        user.Name = f"{first_name} {last_name}"
        user.username = bits_id
        user.BITS_ID = bits_id.upper()
        return user