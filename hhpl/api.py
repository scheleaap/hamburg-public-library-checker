from dataclasses import dataclass
from urllib import response
import requests
import xml.etree.ElementTree as et
from datetime import datetime
from enum import Enum, unique
import logging
from datetime import datetime, date

DEFAULT_BASE_URL = "https://zones.buecherhallen.de/app_webuser/WebUserSvc.asmx"

@unique
class LoanStatus(Enum):
    AVAILABLE = 0
    ON_LOAN = 64

@dataclass
class StockItem:
    shelf: str
    loan_status: LoanStatus
    due_date: date | None

@dataclass
class LibraryStock:
    library_name: str
    copies_in_library: int
    stock_items: list[StockItem]

@dataclass
class StockInfo:
    libraries: list[LibraryStock]

class Api:
    def __init__(self, base_url: str = DEFAULT_BASE_URL) -> None:
        self.base_url = base_url

    def get_stock_info(self, item_id: str) -> StockInfo:
        def xml_to_stock_item(xml: et.Element) -> StockItem:
            raw_due_date = xml.find("{*}DueDate").text.strip()
            if raw_due_date:
                due_date = datetime.strptime(raw_due_date, r"%d/%m/%Y").date()
            else:
                due_date = None
            raw_loan_status=int(xml.find("{*}IsOnLoan").text)
            loan_status = LoanStatus(raw_loan_status)
            return StockItem(
                shelf=xml.find("{*}SHELF").text.strip(),
                loan_status=loan_status,
                due_date=due_date,
                )
        
        def xml_to_library_stock(xml: et.Element) -> LibraryStock:
            return LibraryStock(
                library_name=xml.find("{*}Name").text.strip(),
                copies_in_library=int(xml.find("{*}Copies").text),
                stock_items=[xml_to_stock_item(i) for i in xml.findall("./{*}Stock/{*}Items/{*}__Element__")]
            )

        def xml_string_to_stock_info(xml_string) -> StockInfo:
            root = et.fromstring(response.text)
            gssir = root.find(".//{*}GetStockStatusInfoResult")
            return StockInfo(
                libraries=[xml_to_library_stock(library) for library in gssir]
            )

        response = requests.get(f"{self.base_url}/GetStockStatusInfo?BacNo={item_id}&ExpandBranchInfo=1")
        return xml_string_to_stock_info(response.text)
