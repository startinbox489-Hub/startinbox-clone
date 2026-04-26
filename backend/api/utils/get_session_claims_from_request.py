"""
Get session and claims from request
"""

from api.schema.default_response_schema import CustomRequest, AsyncSession, Claims


def get_claims_and_session(request: CustomRequest) -> tuple[AsyncSession, Claims]:
    """
    Gets session and claims from request
    """
    if not request.state.claims or not request.state.session:
        raise RuntimeError("session or claims missing in request object.")
    return request.state.session, request.state.claims
