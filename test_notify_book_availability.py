#!/usr/bin/env python3
import unittest
import logging

from notify_book_availability import AvailabilityInfo, best_availability_info_reducer
from hhpl.api import Status
from datetime import date


class NotifyBookAvailabilityTest(unittest.TestCase):
    def test_best_availability_info_reducer(self):
        ai1 = AvailabilityInfo(
            loan_status=Status.AVAILABLE, due_date=None, library_name=""
        )
        ai2 = AvailabilityInfo(
            loan_status=Status.ON_LOAN, due_date=None, library_name=""
        )
        ai3 = AvailabilityInfo(
            loan_status=Status.ON_LOAN, due_date=date(2022, 2, 1), library_name=""
        )
        ai4 = AvailabilityInfo(
            loan_status=Status.ON_LOAN, due_date=date(2022, 2, 2), library_name=""
        )

        self.assertEqual(best_availability_info_reducer(ai1, ai1), ai1)
        self.assertEqual(best_availability_info_reducer(ai1, ai2), ai1)
        self.assertEqual(best_availability_info_reducer(ai2, ai1), ai1)
        self.assertEqual(best_availability_info_reducer(ai1, ai3), ai1)
        self.assertEqual(best_availability_info_reducer(ai3, ai1), ai1)
        self.assertEqual(best_availability_info_reducer(ai3, ai4), ai3)
        self.assertEqual(best_availability_info_reducer(ai4, ai3), ai3)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
    unittest.main()
