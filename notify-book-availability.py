#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
import logging
import sys
from hhpl.api import Api, LoanStatus, StockInfo, StockItem
from hhpl.util import sensible_due_date

def parse_arguments(raw_args):
    parser = argparse.ArgumentParser(
        description="Notifies that a book is available.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("book_id", help="The id of the book")
    parser.add_argument("--available-only", action="store_true", help="Filter by available books only")

    args = parser.parse_args(raw_args)

    return args

@dataclass
class FlattenedStockItem(StockItem):
    library_name: str

def main(args):
    api = Api()
    si = api.get_stock_info(args.book_id)

    def flatten_stock_items(stock_info: StockInfo) -> list[FlattenedStockItem]:
        for l in stock_info.libraries:
            for si in l.stock_items:
                yield FlattenedStockItem(
                    library_name=l.library_name,
                    shelf=si.shelf,
                    loan_status=si.loan_status,
                    due_date=sensible_due_date(si.due_date, si.loan_status)
                )
    
    fsi = flatten_stock_items(si)
    for i in fsi:
        if not args.available_only or (args.available_only and i.loan_status is LoanStatus.AVAILABLE):
            print(f"{i.library_name} {i.loan_status} {i.due_date}")

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(message)s"
    )

if __name__ == "__main__":
    setup_logging()
    main(parse_arguments(sys.argv[1:]))
