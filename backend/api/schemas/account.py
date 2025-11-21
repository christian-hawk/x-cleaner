"""
Pydantic schemas for account-related API requests and responses.

Defines data models for account endpoints following REST API best practices.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AccountBase(BaseModel):
    """Base schema with common account fields."""

    user_id: str = Field(..., description="X account user ID")
    username: str = Field(..., description="X account username")
    display_name: str = Field(..., description="Account display name")
    bio: Optional[str] = Field(None, description="Account bio/description")
    verified: bool = Field(False, description="Account verification status")
    followers_count: int = Field(0, ge=0, description="Number of followers")
    following_count: int = Field(0, ge=0, description="Number of accounts following")
    tweet_count: int = Field(0, ge=0, description="Total number of tweets")
    location: Optional[str] = Field(None, description="Account location")
    website: Optional[str] = Field(None, description="Account website URL")
    profile_image_url: Optional[str] = Field(None, description="Profile image URL")


class AccountResponse(AccountBase):
    """Schema for account response with categorization data."""

    category: str = Field(..., description="Assigned category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Categorization confidence score")
    reasoning: str = Field("", description="AI reasoning for categorization")
    created_at: Optional[datetime] = Field(None, description="Account creation date")
    analyzed_at: Optional[datetime] = Field(None, description="Analysis/categorization timestamp")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "123456789",
                "username": "elonmusk",
                "display_name": "Elon Musk",
                "bio": "Technoking of Tesla",
                "verified": True,
                "followers_count": 150000000,
                "following_count": 500,
                "tweet_count": 25000,
                "location": "Austin, TX",
                "website": "https://tesla.com",
                "profile_image_url": "https://pbs.twimg.com/profile_images/...",
                "category": "Tech Entrepreneurs & Founders",
                "confidence": 0.95,
                "reasoning": "CEO of multiple tech companies, active in tech community",
                "created_at": "2020-01-01T00:00:00Z",
                "analyzed_at": "2025-01-20T15:30:00Z"
            }
        }


class AccountListResponse(BaseModel):
    """Schema for paginated account list response."""

    accounts: list[AccountResponse] = Field(..., description="List of accounts")
    total: int = Field(..., ge=0, description="Total number of accounts")
    category: Optional[str] = Field(None, description="Filter category if applied")
