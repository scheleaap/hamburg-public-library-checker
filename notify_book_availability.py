#!/usr/bin/env python3

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from email.policy import default
from functools import reduce
from hhpl.api import Api, Status, CatalogInfo, Copy
from hhpl.util import sensible_due_date
import argparse
import logging
import os.path
import pickle
import requests
import sys

# import http.client as http_client
# http_client.HTTPConnection.debuglevel = 1


def parse_arguments(raw_args):
    parser = argparse.ArgumentParser(
        description="Notifies that a book is available.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("catalog_number", help="The catalog number of the book")

    args = parser.parse_args(raw_args)

    return args


@dataclass
class AvailabilityInfo:
    library_name: str
    loan_status: Status
    due_date: date | None


class Notifier:
    def book_is_available(self, catalog_number: str):
        pass


class StdoutNotifier(Notifier):
    def book_is_available(self, catalog_info: CatalogInfo):
        logging.info(f"Book '{catalog_info.title}' is available. Go get it now!")


class IftttNotifier(Notifier):
    def __init__(self, key: str) -> None:
        self.key = key

    def book_is_available(self, catalog_info: CatalogInfo):
        payload = {
            "value1": "Book available",
            "value2": f"Book '{catalog_info.title}' is available!",
            "value3": f"https://www.buecherhallen.de/suchergebnis-detail/medium/{catalog_info.catalog_number}.html",
        }
        response = requests.post(
            f"https://maker.ifttt.com/trigger/hhpl/with/key/{self.key}", json=payload
        )


class State:
    file_name = "state.pkl"

    @classmethod
    def load(cls):
        """Loads saved state or return a new state."""
        if os.path.exists(State.file_name):
            with open("state.pkl", "rb") as f:
                return pickle.loads(f)
        else:
            return State()

    def __init__(self) -> None:
        self.loan_status = defaultdict(lambda: Status.ON_LOAN)

    def set_loan_status(self, catalog_number: str, new_loan_status: bool):
        old_loan_status = self.loan_status[catalog_number]
        self.loan_status[catalog_number] = new_loan_status
        if old_loan_status == new_loan_status:
            return None
        else:
            return (old_loan_status, new_loan_status)


def main(args):
    api = Api()
    notifiers = [
        StdoutNotifier(),
        IftttNotifier(key="dZHnJC5lfc1wE8l6TYNUYDxEBRHuUJ8uvobc7QFP3KP"),
    ]
    state = State.load()
    logging.debug(f"State at startup: {state}")

    def copies_to_availability_infos(copies: list[Copy]) -> list[AvailabilityInfo]:
        for copy in copies:
            yield AvailabilityInfo(
                library_name=copy.owner_description,
                loan_status=copy.current_status,
                due_date=sensible_due_date(copy.status_change_date, copy.current_status),
            )

    (catalog_info, copies) = api.get_catalog_info(args.catalog_number)

    ais = copies_to_availability_infos(copies)

    best_availability = reduce(best_availability_info_reducer, ais)

    change = state.set_loan_status(
        catalog_number=args.catalog_number,
        new_loan_status=best_availability.loan_status,
    )
    if change and change[1] == Status.AVAILABLE:
        for notifier in notifiers:
            notifier.book_is_available(catalog_info)

    # logging.debug(f"State at end: {state}")
    # state = State.load()


def setup_logging(level):
    logging.basicConfig(level=level, format="%(message)s")


def best_availability_info_reducer(
    a: AvailabilityInfo, b: AvailabilityInfo
) -> AvailabilityInfo:
    if a.loan_status.value < b.loan_status.value:
        return a
    elif a.loan_status.value > b.loan_status.value:
        return b
    elif a.due_date is None and b.due_date is None:
        return a
    elif a.due_date is None:
        return b
    elif b.due_date is None:
        return a
    elif a.due_date <= b.due_date:
        return a
    else:
        return b


if __name__ == "__main__":
    setup_logging(logging.INFO)
    main(parse_arguments(sys.argv[1:]))
