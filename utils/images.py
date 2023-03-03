from middlewares.middlewares import RequestMiddleware

def image_middleware():
    custom_request = RequestMiddleware(get_response=None)
    custom_request = custom_request.thread_local.current_request
    url_image = 'https://' + custom_request.META['HTTP_HOST']
    return url_image