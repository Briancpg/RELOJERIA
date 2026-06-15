from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    currency: str
    week_start: date
    week_end: date
    total_weekly: Decimal
    total_monthly: Decimal
    floating_weekly: Decimal
    floating_monthly: Decimal
    floating_profit: Decimal
    pending_repairs: int
    delivered_repairs: int
    accumulated_profit: Decimal
    active_repairs: int
    ready_repairs: int
    delivered_weekly: int


class JewelryDashboardSummary(BaseModel):
    sent_repairs: int
    in_process_repairs: int
    ready_repairs: int
    delivered_repairs: int


class StatusCount(BaseModel):
    status: str
    count: int


class WeeklyProfit(BaseModel):
    week_start: date
    week_end: date
    total_profit: Decimal
