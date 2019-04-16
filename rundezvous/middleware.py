class LocationMiddleware:
    """
    Automatically updates user's location for every request
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        location = request.META.get('GPS_LOCATION')
        user = request.user

        if location is not None:
            if user.location != location:
                user.update_location(location)

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
