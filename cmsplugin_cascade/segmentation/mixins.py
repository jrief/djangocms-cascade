# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model


class EmulateUser(object):
    def get_context_override(self, request):
        """
        Override the request object with an emulated user.
        """
        context_override = super(EmulateUser, self).get_context_override(request)
        try:
            if request.user.is_staff:
                UserModel = get_user_model()
                user = UserModel.objects.get(pk=request.session['emulate_user_id'])
                context_override.update(user=user)
        except (UserModel.DoesNotExist, KeyError):
            pass
        return context_override
