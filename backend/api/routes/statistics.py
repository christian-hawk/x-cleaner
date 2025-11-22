"""
FastAPI routes for statistics and analytics endpoints.

Provides REST API endpoints for statistical analysis and metrics.
"""

from fastapi import APIRouter, Depends

from backend.api.schemas.statistics import (
    CategoryStatistics,
    CategoryStatisticsResponse,
    EngagementMetricsResponse,
    OverallStatisticsResponse,
)
from backend.core.services.statistics_service import StatisticsService
from backend.dependencies import get_statistics_service

router = APIRouter(prefix="/api/statistics", tags=["statistics"])


@router.get("/overall", response_model=OverallStatisticsResponse)
async def get_overall_statistics(
    statistics_service: StatisticsService = Depends(get_statistics_service),
) -> OverallStatisticsResponse:
    """
    Get overall statistics for all accounts.

    Args:
        statistics_service: Injected statistics service.

    Returns:
        Overall statistics including totals, averages, and rates.
    """
    statistics = statistics_service.calculate_overall_statistics()

    return OverallStatisticsResponse(**statistics)


@router.get("/categories", response_model=CategoryStatisticsResponse)
async def get_category_statistics(
    statistics_service: StatisticsService = Depends(get_statistics_service),
) -> CategoryStatisticsResponse:
    """
    Get statistics for each category.

    Args:
        statistics_service: Injected statistics service.

    Returns:
        Per-category statistics sorted by account count.
    """
    category_stats = statistics_service.calculate_category_statistics()

    category_statistics = [
        CategoryStatistics(**stat)
        for stat in category_stats
    ]

    return CategoryStatisticsResponse(categories=category_statistics)


@router.get("/engagement", response_model=EngagementMetricsResponse)
async def get_engagement_metrics(
    statistics_service: StatisticsService = Depends(get_statistics_service),
) -> EngagementMetricsResponse:
    """
    Get engagement-related metrics.

    Args:
        statistics_service: Injected statistics service.

    Returns:
        Engagement metrics including ratios and medians.
    """
    metrics = statistics_service.calculate_engagement_metrics()

    return EngagementMetricsResponse(**metrics)
