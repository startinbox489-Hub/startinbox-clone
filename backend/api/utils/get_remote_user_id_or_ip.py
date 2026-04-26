from api.schema.default_response_schema import CustomRequest
from api.utils.get_client_ip import get_client_ip_render


def get_user_id_or_remote_address(request: CustomRequest) -> str:
    """
    Returns the user_id if user is authenticated or
     the ip address for the current request (or 127.0.0.1 if none found)
     based on the X-Forwarded-For headers.
     Note that a more robust method for determining IP address of the client is
     provided by uvicorn's ProxyHeadersMiddleware.
    """

    ip = get_client_ip_render(request=request)
    user_id = (
        request.state.current_user if hasattr(request.state, "current_user") else None
    )
    return user_id or ip
