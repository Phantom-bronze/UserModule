"""
Authentication Router
=====================

Handles user authentication and authorization:
- Google OAuth SSO flow
- JWT token management (access & refresh)
- User login/logout
- Token refresh

Authentication Flow:
1. User initiates Google OAuth
2. Redirect to Google consent screen
3. Google redirects back with auth code
4. Exchange code for tokens
5. Create/update user in database
6. Return JWT tokens to client
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow
import logging
import json
from typing import Dict

from app.database import get_db
from app.config import settings
from app.models.user import User, UserRole
from app.schemas.auth import (
    TokenResponse,
    RefreshTokenRequest,
    GoogleAuthURL
)
from app.utils.auth import (
    create_token_response,
    refresh_access_token,
    verify_token,
    get_current_user
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# Google OAuth Configuration
# ============================================================

def get_google_oauth_flow():
    """
    Create Google OAuth flow for authentication.

    Returns:
        Flow: Google OAuth flow instance
    """
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        },
        scopes=settings.GOOGLE_SCOPES
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    return flow


# ============================================================
# Authentication Endpoints
# ============================================================

@router.get(
    "/google/login",
    response_model=GoogleAuthURL,
    summary="Initiate Google OAuth login"
)
async def google_login(invitation_token: str = None):
    """
    Initiate Google OAuth authentication flow.

    This endpoint generates the Google OAuth URL that the client
    should redirect the user to for authentication.

    Args:
        invitation_token: Optional invitation token if user is accepting invitation

    Returns:
        GoogleAuthURL: Object containing the authorization URL

    Example:
        GET /api/v1/auth/google/login
        Response: {"auth_url": "https://accounts.google.com/o/oauth2/auth?..."}
    """
    try:
        flow = get_google_oauth_flow()

        # Add invitation token to state if provided
        state = invitation_token if invitation_token else None

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'
        )

        logger.info(f"Generated Google OAuth URL")

        return GoogleAuthURL(auth_url=authorization_url)

    except Exception as e:
        logger.error(f"Failed to generate OAuth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Google authentication"
        )


@router.get(
    "/google/callback",
    summary="Google OAuth callback"
)
async def google_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback.

    This endpoint is called by Google after user grants permissions.
    It exchanges the auth code for tokens, creates/updates the user,
    and returns JWT tokens.

    Args:
        code: Authorization code from Google
        state: State parameter (may contain invitation token)
        error: Error message if OAuth failed
        db: Database session

    Returns:
        JSONResponse: JWT tokens and user information

    Flow:
        1. Exchange code for Google tokens
        2. Verify Google ID token
        3. Extract user info
        4. Create or update user in database
        5. Generate JWT tokens
        6. Return tokens to client
    """
    # Check for OAuth errors
    if error:
        logger.error(f"Google OAuth error: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google authentication failed: {error}"
        )

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided"
        )

    try:
        # Exchange code for tokens
        flow = get_google_oauth_flow()
        flow.fetch_token(code=code)

        # Get credentials
        credentials = flow.credentials

        # Verify the ID token
        idinfo = id_token.verify_oauth2_token(
            credentials.id_token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        # Extract user information
        google_user_id = idinfo.get('sub')
        email = idinfo.get('email')
        full_name = idinfo.get('name', email)
        profile_picture = idinfo.get('picture')

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )

        logger.info(f"Google OAuth successful for {email}")

        # Check if user exists
        user = db.query(User).filter(User.email == email).first()

        if user:
            # Update existing user
            user.google_id = google_user_id
            user.profile_picture_url = profile_picture
            user.update_last_login()

            logger.info(f"Updated existing user: {email}")

        else:
            # Check if this is an invitation flow
            if state:  # state contains invitation token
                # TODO: Validate invitation token and get role/company from invitation
                # For now, create as regular user
                logger.info(f"Creating new user from invitation: {email}")

            # Check if this is the first user (should be super admin)
            user_count = db.query(User).count()

            if user_count == 0:
                # First user is super admin
                user = User(
                    email=email,
                    google_id=google_user_id,
                    full_name=full_name,
                    profile_picture_url=profile_picture,
                    role=UserRole.SUPER_ADMIN,
                    company_id=None,
                    is_active=True
                )
                logger.info(f"Created first user as super admin: {email}")

            else:
                # Regular users must be invited
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Registration is by invitation only. Please contact your administrator."
                )

            user.update_last_login()
            db.add(user)

        db.commit()
        db.refresh(user)

        # Generate JWT tokens
        token_response = create_token_response(user)

        logger.info(f"Login successful for {email}")

        # Return HTML page with JavaScript to store tokens and redirect
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Successful</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .container {{
                    background: white;
                    padding: 2rem;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .spinner {{
                    border: 3px solid #f3f3f3;
                    border-top: 3px solid #4CAF50;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 20px auto;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
                h2 {{ color: #333; margin-bottom: 10px; }}
                p {{ color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="spinner"></div>
                <h2>Login Successful!</h2>
                <p>Redirecting to dashboard...</p>
            </div>
            <script>
                // Store tokens in localStorage
                const authData = {json.dumps(token_response)};

                // Store access token
                localStorage.setItem('access_token', authData.access_token);

                // Store refresh token
                if (authData.refresh_token) {{
                    localStorage.setItem('refresh_token', authData.refresh_token);
                }}

                // Store user data
                if (authData.user) {{
                    localStorage.setItem('user_data', JSON.stringify(authData.user));
                }}

                // Redirect to dashboard after a short delay
                setTimeout(() => {{
                    window.location.href = '/';
                }}, 1000);
            </script>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback failed: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token"
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    When the access token expires, clients can use their refresh token
    to obtain a new access token without requiring the user to log in again.

    Args:
        request: Request containing refresh token
        db: Database session

    Returns:
        TokenResponse: New access and refresh tokens

    Example:
        POST /api/v1/auth/refresh
        Body: {"refresh_token": "eyJ..."}
        Response: {
            "access_token": "eyJ...",
            "refresh_token": "eyJ...",
            "token_type": "bearer",
            ...
        }
    """
    try:
        token_response = await refresh_access_token(request.refresh_token, db)
        return JSONResponse(content=token_response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user"
)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user.

    Note: Since we're using JWT tokens, actual logout is handled client-side
    by removing the tokens. This endpoint is provided for completeness and
    can be used for audit logging.

    Args:
        current_user: Currently authenticated user

    Returns:
        dict: Logout confirmation

    Example:
        POST /api/v1/auth/logout
        Headers: Authorization: Bearer <token>
        Response: {"message": "Logged out successfully"}
    """
    logger.info(f"User logged out: {current_user.email}")

    # TODO: Add to audit log
    # In a more sophisticated system, you might:
    # - Add token to blacklist
    # - Update last_logout timestamp
    # - Log the event

    return {
        "message": "Logged out successfully",
        "user_id": str(current_user.id)
    }


@router.get(
    "/me",
    summary="Get current user"
)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get currently authenticated user information.

    Returns detailed information about the logged-in user.

    Args:
        current_user: Currently authenticated user

    Returns:
        dict: User information

    Example:
        GET /api/v1/auth/me
        Headers: Authorization: Bearer <token>
        Response: {
            "id": "uuid",
            "email": "user@example.com",
            "full_name": "John Doe",
            "role": "admin",
            ...
        }
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "profile_picture_url": current_user.profile_picture_url,
        "role": current_user.role.value,
        "company_id": str(current_user.company_id) if current_user.company_id else None,
        "can_add_devices": current_user.can_add_devices,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }


@router.post(
    "/verify-token",
    summary="Verify access token"
)
async def verify_access_token(token: str):
    """
    Verify if an access token is valid.

    This endpoint can be used by other services to validate tokens.

    Args:
        token: JWT access token to verify

    Returns:
        dict: Token validity status and payload

    Example:
        POST /api/v1/auth/verify-token
        Body: {"token": "eyJ..."}
        Response: {"valid": true, "user_id": "uuid", ...}
    """
    try:
        payload = verify_token(token, "access")

        return {
            "valid": True,
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "company_id": payload.get("company_id"),
            "expires_at": payload.get("exp")
        }

    except HTTPException:
        return {
            "valid": False,
            "error": "Invalid or expired token"
        }
