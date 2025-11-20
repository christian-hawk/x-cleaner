"""
Data models for X-Cleaner application.

This module defines the Pydantic models used throughout the application
for data validation, serialization, and API contracts.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class XAccount(BaseModel):
    """
    X Account data model.

    Represents basic account information fetched from X API.
    """

    user_id: str
    username: str
    display_name: str
    bio: Optional[str] = None
    verified: bool = False
    created_at: Optional[datetime] = None
    followers_count: int = 0
    following_count: int = 0
    tweet_count: int = 0
    location: Optional[str] = None
    website: Optional[str] = None
    profile_image_url: Optional[str] = None


class CategorizedAccount(XAccount):
    """
    Account with category information.

    Extends XAccount with AI-generated category data.
    """

    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: Optional[str] = None
    analyzed_at: datetime = Field(default_factory=datetime.now)


class CategoryStats(BaseModel):
    """
    Statistics for a category.

    Contains aggregated metrics and top accounts for a discovered category.
    """

    name: str
    count: int
    percentage: float
    top_accounts: list[XAccount]
    avg_followers: float
    verification_rate: float


class AnalysisReport(BaseModel):
    """
    Complete analysis report.

    Comprehensive report containing all analysis results and statistics.
    """

    total_accounts: int
    categories_count: int
    analyzed_date: datetime
    category_stats: list[CategoryStats]
    overall_metrics: dict[str, Any]
