from datetime import date
from .api import Status


def sensible_due_date(original: date, status: Status) -> date | None:
    now = date.today()
    if original and status is Status.AVAILABLE:
        return None
    elif original and original < now:
        return None
    else:
        return original
