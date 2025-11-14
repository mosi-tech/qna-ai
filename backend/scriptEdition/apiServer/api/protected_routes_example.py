#!/usr/bin/env python3
"""
Example of how to protect your existing routes with Appwrite auth
This shows how to add authentication and role-based access control
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any
import logging

# Import your existing auth system (now Appwrite-enabled)
from .auth import UserContext, require_authenticated_user, require_premium, require_admin, get_optional_user
from .models import QuestionRequest, AnalysisResponse

logger = logging.getLogger("protected-routes")

# Create router
router = APIRouter()

# Example 1: Public endpoint (no auth required)
@router.get("/public/health")
async def health_check():
    """Public health check - no auth required"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# Example 2: Require any authenticated user
@router.post("/analysis/basic")
async def basic_analysis(
    request: QuestionRequest,
    user: UserContext = Depends(require_authenticated_user)
) -> AnalysisResponse:
    """
    Basic analysis - requires authentication but no specific role
    Any logged-in user can access this
    """
    logger.info(f"Basic analysis requested by {user.email}")
    
    # Your existing analysis logic here
    # The user context is available with all user info
    result = {
        "message": f"Analysis for {user.name}",
        "user_id": user.user_id,
        "question": request.question
    }
    
    return AnalysisResponse(success=True, data=result)

# Example 3: Require premium role
@router.post("/analysis/premium")
async def premium_analysis(
    request: QuestionRequest,
    user: UserContext = Depends(require_premium)
) -> AnalysisResponse:
    """
    Premium analysis features - requires premium role
    Only users with 'premium' role can access
    """
    logger.info(f"Premium analysis requested by {user.email} with roles: {user.roles}")
    
    # Your existing premium analysis logic here
    result = {
        "message": f"Premium analysis for {user.name}",
        "user_id": user.user_id,
        "question": request.question,
        "premium_features": ["advanced_analytics", "real_time_data", "custom_models"]
    }
    
    return AnalysisResponse(success=True, data=result)

# Example 4: Admin-only endpoint
@router.get("/admin/users")
async def list_users(
    user: UserContext = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Admin endpoint - requires admin role
    Only users with 'admin' role can access
    """
    logger.info(f"Admin user list requested by {user.email}")
    
    # Your existing admin logic here
    return {
        "message": f"Admin data accessed by {user.name}",
        "users": ["user1", "user2", "user3"],  # Example data
        "admin_user": user.email
    }

# Example 5: Optional authentication
@router.get("/public/stats")
async def public_stats(
    user: UserContext = Depends(get_optional_user)
) -> Dict[str, Any]:
    """
    Public stats - authentication optional
    Behavior changes based on whether user is logged in
    """
    if user:
        logger.info(f"Stats requested by authenticated user: {user.email}")
        # Show personalized stats for logged-in users
        return {
            "stats": {"total_analyses": 1000, "user_analyses": 45},
            "user": {"name": user.name, "email": user.email}
        }
    else:
        logger.info("Stats requested by anonymous user")
        # Show only public stats for anonymous users
        return {
            "stats": {"total_analyses": 1000},
            "user": None
        }

# Example 6: Manual role checking within endpoint
@router.post("/analysis/flexible")
async def flexible_analysis(
    request: QuestionRequest,
    user: UserContext = Depends(require_authenticated_user)
) -> AnalysisResponse:
    """
    Flexible analysis with manual role checking
    Different features based on user's role
    """
    logger.info(f"Flexible analysis requested by {user.email} with roles: {user.roles}")
    
    # Base analysis available to all authenticated users
    features = ["basic_analysis"]
    
    # Add features based on roles
    if user.has_role("premium"):
        features.extend(["advanced_charts", "real_time_data"])
    
    if user.has_role("admin"):
        features.extend(["admin_insights", "system_metrics"])
    
    result = {
        "message": f"Analysis for {user.name}",
        "user_id": user.user_id,
        "question": request.question,
        "available_features": features,
        "user_roles": user.roles
    }
    
    return AnalysisResponse(success=True, data=result)

# Example 7: How to update your existing routes
"""
To protect your existing routes, simply add the auth dependency:

BEFORE:
@router.post("/api/analyze")
async def analyze_question(request: QuestionRequest):
    # Your existing code

AFTER:
@router.post("/api/analyze")
async def analyze_question(
    request: QuestionRequest,
    user: UserContext = Depends(require_authenticated_user)  # Add this line
):
    # Your existing code
    # Now you have access to user.user_id, user.email, user.roles, etc.

For premium features:
@router.post("/api/analyze-premium")
async def analyze_premium(
    request: QuestionRequest,
    user: UserContext = Depends(require_premium)  # Requires premium role
):
    # Premium analysis code

For admin features:
@router.post("/api/admin/manage")
async def admin_manage(
    request: AdminRequest,
    user: UserContext = Depends(require_admin)  # Requires admin role
):
    # Admin-only code
"""