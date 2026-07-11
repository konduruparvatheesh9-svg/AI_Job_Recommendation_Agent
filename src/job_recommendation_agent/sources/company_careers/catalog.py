"""Verified official career portals for priority employers."""

from typing import NamedTuple


class CareerPortal(NamedTuple):
    """A public company-operated career search entry point."""

    company: str
    url: str


PRIORITY_CAREER_PORTALS = (
    CareerPortal("ZEISS", "https://jobs.zeiss.com/"),
    CareerPortal("Bosch", "https://jobs.bosch.com/"),
    CareerPortal("Siemens", "https://jobs.siemens.com/"),
    CareerPortal("Infineon", "https://jobs.infineon.com/careers"),
    CareerPortal("SAP", "https://jobs.sap.com/"),
    CareerPortal("GlobalFoundries", "https://careers.globalfoundries.com/"),
    CareerPortal("ASML", "https://www.asml.com/en/careers/find-your-job"),
    CareerPortal("BMW Group", "https://www.bmwgroup.jobs/"),
    CareerPortal("Microsoft", "https://jobs.careers.microsoft.com/global/en/search"),
    CareerPortal("Amazon", "https://www.amazon.jobs/en/search"),
)
