"""Resolve calendar 'today' from client local date (avoids UTC server drift)."""
from datetime import date


def parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def resolve_today(request=None, explicit_date=None):
    """Prefer client ?date= or X-Local-Date header, else server date."""
    if explicit_date:
        d = parse_date(explicit_date)
        if d:
            return d
    if request is not None:
        d = parse_date(request.args.get("date"))
        if d:
            return d
        d = parse_date(request.headers.get("X-Local-Date"))
        if d:
            return d
    return date.today()


def today_iso(request=None, explicit_date=None):
    return resolve_today(request, explicit_date).isoformat()


def weekday_index(request=None, explicit_date=None):
    return resolve_today(request, explicit_date).weekday()
