from credyapp.models import RequestCounter


class RequestCountMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        req_counter = RequestCounter.objects.last()
        if req_counter:
            req_counter.counter += 1
            req_counter.save()
        else:
            RequestCounter.objects.create(counter=1)

        response = self.get_response(request)

        return response
