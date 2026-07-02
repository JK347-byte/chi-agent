from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from config import PROJECTS, QUOTA_WARNING_DAYS


def get_rules(project: str) -> dict:
    return PROJECTS.get(project, {})


def year_window(enrollment_date: date, ref: date = None) -> tuple[date, date]:
    """回傳個案當前年度的起訖日（以收案日為基準）"""
    if ref is None:
        ref = date.today()
    years = 0
    while True:
        start = enrollment_date + relativedelta(years=years + 1)
        if start > ref:
            break
        years += 1
    window_start = enrollment_date + relativedelta(years=years)
    window_end = window_start + relativedelta(years=1) - timedelta(days=1)
    return window_start, window_end


def visits_in_window(visit_dates: list[date], start: date, end: date) -> list[date]:
    return [v for v in visit_dates if start <= v <= end]


def earliest_next_date(last_date: date, project: str, is_first: bool) -> date:
    rules = get_rules(project)
    interval = rules["first_interval_days"] if is_first else rules["subsequent_interval_days"]
    return last_date + timedelta(days=interval)


def suggest_next_date(enrollment_date: date, all_visits: list, project: str):
    """計算下次最早可回診日，考慮年度額度"""
    rules = get_rules(project)
    today = date.today()

    w_start, w_end = year_window(enrollment_date, today)
    this_year_visits = visits_in_window(all_visits, w_start, w_end)

    if len(this_year_visits) >= rules["max_visits_per_year"]:
        # 本年度已滿，計算下一年度
        next_w_start = w_end + timedelta(days=1)
        next_w_end = next_w_start + relativedelta(years=1) - timedelta(days=1)
        next_year_visits = visits_in_window(all_visits, next_w_start, next_w_end)
        if len(next_year_visits) >= rules["max_visits_per_year"]:
            return None
        base_date = next_w_start
        is_first = len(all_visits) == 0
    else:
        base_date = all_visits[-1] if all_visits else enrollment_date
        is_first = len(all_visits) == 0

    return earliest_next_date(base_date, project, is_first)


def quota_warning(enrollment_date: date, all_visits: list[date], project: str) -> bool:
    """是否需要發出年度額度即將到期警告"""
    rules = get_rules(project)
    today = date.today()
    w_start, w_end = year_window(enrollment_date, today)
    used = len(visits_in_window(all_visits, w_start, w_end))
    remaining_quota = rules["max_visits_per_year"] - used
    days_left = (w_end - today).days
    return remaining_quota > 0 and 0 < days_left <= QUOTA_WARNING_DAYS
