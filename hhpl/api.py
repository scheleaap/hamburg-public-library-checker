from dataclasses import dataclass
from urllib import response
import requests
import xml.etree.ElementTree as et
from datetime import datetime
from enum import Enum, auto, unique
import logging
from datetime import datetime, date

DEFAULT_BASE_URL = "https://zones.buecherhallen.de/app_webuser/WebUserSvc.asmx"


@unique
class Status(Enum):
    AVAILABLE = auto()
    ON_LOAN = auto()

    @classmethod
    def from_code(cls, catalog_number: str, code: int):
        # Current understanding:
        # 0 = available
        # 10 = on loan
        # 11 = available (but somehow different)
        # 16 = on loan but overdue
        if code in [0, 11]:
            return Status.AVAILABLE
        elif code in [10, 16]:
            return Status.ON_LOAN
        else:
            raise ValueError(f"Unknown status code {code} for book {catalog_number}")


@dataclass
class Copy:
    copy_number: str
    owner_description: str
    current_status: Status
    status_change_date: date | None
    is_reserved: bool


@dataclass
class CatalogInfo:
    catalog_number: str
    title: str
    author: str
    year_of_publication: int
    number_of_copies: int


class Api:
    def __init__(self, base_url: str = DEFAULT_BASE_URL) -> None:
        self.base_url = base_url

    def get_catalog_info(self, catalog_number: str) -> tuple[CatalogInfo, list[Copy]]:
        def xml_to_copy(xml) -> Copy:
            raw_status = int(xml.find("{*}CurrentStatus").text)
            status = Status.from_code(code=raw_status, catalog_number=catalog_number)
            raw_status_change_date = xml.find("{*}StatusChangeDate").text.strip()
            status_change_date = datetime.strptime(raw_status_change_date, r"%d/%m/%Y").date()
            return Copy(
                copy_number=xml.find("{*}ItemNo").text.strip(),
                owner_description=xml.find("{*}OwnerDescription").text.strip(),
                current_status=status,
                status_change_date=status_change_date,
                is_reserved=bool(int(xml.find("{*}IsReserved").text)),
            )

        def xml_string_to_catalog_info(xml_string) -> CatalogInfo:
            root = et.fromstring(response.text)
            xml = root.find(".//{*}Items")
            items = xml.findall("{*}Item")
            return (
                CatalogInfo(
                    catalog_number=catalog_number,
                    title=xml.find("{*}Title").text.strip(),
                    author=xml.find("{*}Author").text.strip(),
                    year_of_publication=int(xml.find("{*}YearOfPublication").text),
                    number_of_copies=int(xml.find("{*}TotalItems").text),
                ),
                [xml_to_copy(item) for item in items],
            )

        response = requests.get(
            f"{self.base_url}/GetCatalogueItems?CatalogueNumber={catalog_number}"
        )
        return xml_string_to_catalog_info(response.text)
