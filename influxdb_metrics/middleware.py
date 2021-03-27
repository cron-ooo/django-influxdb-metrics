import logging
import time

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from tld import get_tld
from tld.exceptions import TldBadUrl, TldDomainNotFound, TldIOError

from .loader import measurement_name_for, write_points

logger = logging.getLogger(__name__)


class InfluxDBRequestMiddleware:
    """
    Measures request time and sends metric to InfluxDB.

    Credits go to: https://github.com/andymckay/django-statsd/blob/master/django_statsd/middleware.py#L24  # NOQA

    """

    def __init__(self, get_response=None):
        if getattr(settings, 'INFLUXDB_DISABLED', False):
            raise MiddlewareNotUsed

        self.get_response = get_response

    def __call__(self, request):
        request._start_time = time.perf_counter_ns()
        response = self.get_response(request)
        if hasattr(request, '_view_module'):
            self._record_time(request)
        return response

    @staticmethod
    def process_view(request, view_func, view_args, view_kwargs):
        request._view_module = view_func.__module__
        request._view_name = getattr(view_func, '__name__', view_func.__class__.__name__)

    @staticmethod
    def _record_time(request):
        ms = (time.perf_counter_ns() - request._start_time) // 1_000_000

        referer = request.META.get('HTTP_REFERER')
        referer_tld = None
        if referer:
            try:
                referer_tld = get_tld(referer, as_object=True)
            except (TldBadUrl, TldDomainNotFound, TldIOError):
                pass

        # This allows you to measure click rates for ad-campaigns, just
        # make sure that your ads have `?campaign=something` in the URL
        campaign_keyword = getattr(
            settings, 'INFLUXDB_METRICS_CAMPAIGN_KEYWORD', 'campaign',
        )
        campaign = request.GET.getlist(campaign_keyword, [''])[0]

        data = [{
            'measurement': measurement_name_for('request'),
            'tags': {
                'host': settings.INFLUXDB_TAGS_HOST,
                'is_ajax': request.is_ajax(),
                'is_authenticated': request.user.is_authenticated,
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser,
                'method': request.method,
                'module': request._view_module,
                'view': request._view_name,
                'referer': referer,
                'referer_tld': referer_tld.tld if referer_tld else '',
                'full_path': request.get_full_path_info(),
                'path': request.path_info,
                'campaign': campaign,
                'scheme': request.scheme,
                'content_type': request.headers.get('content-type'),
            },
            'fields': {'value': ms},
        }]
        try:
            write_points(data)
        except Exception as err:
            logger.exception(err, extra={"request": request})
            # sadly, when using celery, there can be issues with the connection to the MQ. Better to drop the data
            # than fail the request.
