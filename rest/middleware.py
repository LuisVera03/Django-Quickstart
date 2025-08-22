import time
from django.utils.deprecation import MiddlewareMixin

class ExecutionTimeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Save the start time when the request arrives
        request.start_time = time.time()

    def process_response(self, request, response):
        # Calculate the elapsed time
        if hasattr(request, "start_time"):
            elapsed = time.time() - request.start_time
            # Print to console
            print(f"Execution time: {elapsed:.4f} seconds - {request.path}")
            # Optional: add the elapsed time as a response header
            response["X-Execution-Time"] = f"{elapsed:.4f}s"
        return response