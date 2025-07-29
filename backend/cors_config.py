"""
CORS Configuration Utility
Provides flexible CORS settings for development and production
"""

def get_cors_origins(development=True):
    """
    Get CORS origins based on environment
    
    Args:
        development (bool): If True, allows all localhost ports for development
    
    Returns:
        list: List of allowed origins
    """
    if development:
        # Allow all localhost ports for development
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001", 
            "http://127.0.0.1:3001",
            "http://localhost:3002",
            "http://127.0.0.1:3002",
            "http://localhost:3003",
            "http://127.0.0.1:3003",
            "http://localhost:3004",
            "http://127.0.0.1:3004",
            "http://localhost:3005",
            "http://127.0.0.1:3005",
        ]
    else:
        # Production origins - add your production domains here
        return [
            "https://your-production-domain.com",
            "https://www.your-production-domain.com"
        ]

def get_flask_cors_config():
    """Get CORS configuration for Flask"""
    return {
        "origins": get_cors_origins(),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True
    }

def get_fastapi_cors_config():
    """Get CORS configuration for FastAPI"""
    return {
        "allow_origins": get_cors_origins(),
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    } 