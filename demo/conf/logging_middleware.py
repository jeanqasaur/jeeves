import logging
from django.db import connection
from django.utils.encoding import smart_str

logger = logging.getLogger(__name__)

# Based off of https://djangosnippets.org/snippets/290/

class ConfLoggingMiddleware(object):
    def process_request(self, request):
        pass

    def process_response(self, request, response):
        logger.info("%s \"%s\" (%s)" % (request.method, smart_str(request.path_info), response.status_code))

        indentation = 2
        if len(connection.queries) > 0:
            total_time = 0.0
            for query in connection.queries:
                nice_sql = query['sql'].replace('"', '').replace(',',', ')
                sql = "[%s] %s" % (query['time'], nice_sql)
                total_time = total_time + float(query['time'])
                logger.info("%s%s\n" % (" "*indentation, sql))
            replace_tuple = (" "*indentation, str(total_time))
            logger.info("%s[TOTAL QUERIES: %d]" % (" "*indentation, len(connection.queries)))
            logger.info("%s[TOTAL TIME: %s seconds]" % replace_tuple)
        return response
