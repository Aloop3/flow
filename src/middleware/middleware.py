import functools
import logging
from typing import Callable, Dict, Any, List
from src.utils.response import create_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class LambdaMiddleware:
    """
    Middleware class for AWS Lambda functions.

    Provides a way to compose multiple middleware functions that wrap Lambda handlers,
    allowing for pre-processing of requests and standardized error handling.
    """

    def __init__(self, handler: Callable):
        """
        Initialize the middleware with a handler function.

        :param handler: The Lambda handler function to wrap
        """
        self.handler = handler
        self.middlewares = []

    def add_middleware(self, middleware: Callable):
        """
        Add a middleware function to the chain.

        :param middleware: A middleware function that takes (event, context) and returns a modified event
        """
        self.middlewares.append(middleware)
        return self

    def __call__(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Execute the middleware chain and the handler.

        :param event: The Lambda event
        :param context: The Lambda context
        :return: The response from the handler after middleware processing
        """
        # Apply middleware pre-processing
        for middleware in self.middlewares:
            try:
                event = middleware(event, context)
            except Exception as e:
                logger.error(f"Middleware error: {str(e)}")
                return create_response(500, {"error": str(e)})

        # Call the handler
        try:
            response = self.handler(event, context)
            return response
        except Exception as e:
            logger.error(f"Handler error: {str(e)}")
            return create_response(500, {"error": str(e)})


def with_middleware(middlewares: List[Callable] = None):
    """
    Decorator to apply middleware to a handler function.

    :param middlewares: List of middleware functions to apply
    :return: Decorated handler function
    """

    def decorator(handler):
        @functools.wraps(handler)
        def wrapper(event, context):
            middleware = LambdaMiddleware(handler)
            if middlewares:
                for middleware_func in middlewares:
                    middleware.add_middleware(middleware_func)
            return middleware(event, context)

        return wrapper

    return decorator
