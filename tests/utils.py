from django.template import RequestContext


def get_request_context(request, extra_context=None):
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request, extra_context)
    # XXX: Workaround for an issue with django-cms that we do not fully
    # understand yet. It seems that the template context processors are not
    # run early enough, so context['request'] is not available when
    # django-cms tries to access it. We should do further analysis on this.
    context['request'] = request
    # The same problem seems to exist with request.user.
    context['user'] = request.user
    return context
