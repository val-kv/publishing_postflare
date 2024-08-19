from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def subscription_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.has_active_subscription():
            return HttpResponseForbidden("Вы должны быть подписчиком, чтобы получить доступ к этой странице.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


@subscription_required
def protected_view(request):
    return render(request, 'protected_page.html')

