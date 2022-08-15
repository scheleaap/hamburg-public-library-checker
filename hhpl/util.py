from datetime import date
from .api import LoanStatus

def sensible_due_date(original: date, loan_status: LoanStatus) -> date | None:
    now = date.today()
    if original and loan_status is LoanStatus.AVAILABLE:
        return None
    elif original and original < now:
        return None
    else:
        return original
