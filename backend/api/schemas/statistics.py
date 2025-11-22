"""
Pydantic schemas for statistics and analytics API responses.

Defines data models for statistical analysis endpoints.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OverallStatisticsResponse(BaseModel):
    """Schema for overall statistics response."""

    total_accounts: int = Field(..., ge=0, description="Total number of accounts")
    total_categories: int = Field(..., ge=0, description="Total number of categories")
    verified_count: int = Field(..., ge=0, description="Number of verified accounts")
    verification_rate: float = Field(..., ge=0.0, le=100.0, description="Verification percentage")
    avg_followers: float = Field(..., ge=0.0, description="Average followers per account")
    avg_following: float = Field(..., ge=0.0, description="Average following per account")
    avg_tweets: float = Field(..., ge=0.0, description="Average tweets per account")
    total_followers: int = Field(..., ge=0, description="Combined follower count")
    total_following: int = Field(..., ge=0, description="Combined following count")
    total_tweets: int = Field(..., ge=0, description="Combined tweet count")
    most_popular_category: Optional[str] = Field(None, description="Category with most accounts")


class CategoryStatistics(BaseModel):
    """Schema for per-category statistics."""

    category: str = Field(..., description="Category name")
    account_count: int = Field(..., ge=0, description="Number of accounts in category")
    percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage of total accounts")
    avg_followers: float = Field(..., ge=0.0, description="Average followers in category")
    verification_rate: float = Field(..., ge=0.0, le=100.0, description="Verification rate in category")


class CategoryStatisticsResponse(BaseModel):
    """Schema for category statistics list response."""

    categories: List[CategoryStatistics] = Field(..., description="List of category statistics")


class EngagementMetricsResponse(BaseModel):
    """Schema for engagement metrics response."""

    avg_follower_following_ratio: float = Field(..., ge=0.0, description="Average follower/following ratio")
    avg_tweets_per_follower: float = Field(..., ge=0.0, description="Average tweets per 1000 followers")
    median_followers: int = Field(..., ge=0, description="Median follower count")
    median_following: int = Field(..., ge=0, description="Median following count")
