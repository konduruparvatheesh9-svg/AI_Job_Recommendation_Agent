"""Verified official career portals for priority employers."""

from typing import NamedTuple


class CareerPortal(NamedTuple):
    """A public company-operated career search entry point."""

    company: str
    url: str
    tier: int
    roles: str


PRIORITY_CAREER_PORTALS = (
    CareerPortal(
        "ZEISS",
        "https://www.zeiss.com/career/en/locations/germany.html",
        1,
        "Data, software, IT, quality and manufacturing analytics",
    ),
    CareerPortal("Bosch", "https://jobs.bosch.com/", 1, "Data, BI, AI, digital transformation"),
    CareerPortal(
        "Volkswagen Group",
        "https://jobs.volkswagen-group.com/",
        1,
        "Data, AI, industrial engineering",
    ),
    CareerPortal(
        "CARIAD",
        "https://cariad.technology/en/careers.html",
        1,
        "AI, product strategy, data analytics",
    ),
    CareerPortal(
        "Munich Re", "https://www.munichre.com/careers/en.html", 1, "AI, data, compliance analytics"
    ),
    CareerPortal(
        "Siemens", "https://jobs.siemens.com/", 1, "Industrial AI, automation, product analytics"
    ),
    CareerPortal(
        "Infineon",
        "https://jobs.infineon.com/careers",
        1,
        "Semiconductor and manufacturing analytics",
    ),
    CareerPortal("ZF", "https://jobs.zf.com/", 1, "Industry 4.0, AI, manufacturing intelligence"),
    CareerPortal(
        "Schaeffler", "https://careers.schaeffler.com/", 1, "Industrial data, process analytics"
    ),
    CareerPortal(
        "Continental",
        "https://www.continental.com/en/career/",
        1,
        "AI, data science, smart manufacturing",
    ),
    CareerPortal("Henkel", "https://www.henkel.com/careers", 1, "Data, ML, digital transformation"),
    CareerPortal("TeamViewer", "https://careers.teamviewer.com/", 2, "Product analytics, data, AI"),
    CareerPortal(
        "Personio", "https://www.personio.com/careers/", 2, "Business and product analytics"
    ),
    CareerPortal("Celonis", "https://www.celonis.com/careers/", 2, "Process mining, data, AI"),
    CareerPortal("DATEV", "https://www.datev.de/web/de/karriere", 2, "BI and data analytics"),
    CareerPortal("SAP", "https://jobs.sap.com/", 2, "Data science, AI, business analytics"),
    CareerPortal("PUMA", "https://about.puma.com/en/jobs", 2, "Data and finance analytics"),
    CareerPortal(
        "Mercedes-Benz",
        "https://group.mercedes-benz.com/careers/",
        2,
        "Digital transformation and data",
    ),
    CareerPortal(
        "BMW Group", "https://www.bmwgroup.jobs/", 2, "Production analytics, AI, data engineering"
    ),
    CareerPortal("Audi", "https://www.audi.com/en/careers/", 2, "Industrial AI and digitalization"),
    CareerPortal("Porsche", "https://jobs.porsche.com/", 2, "Product and manufacturing analytics"),
    CareerPortal("Zalando", "https://jobs.zalando.com/", 3, "Product and data analytics"),
    CareerPortal("HelloFresh", "https://careers.hellofresh.com/", 3, "BI and data analytics"),
    CareerPortal("Delivery Hero", "https://careers.deliveryhero.com/", 3, "Product analytics"),
    CareerPortal("N26", "https://n26.com/en-eu/careers", 3, "Data analytics"),
    CareerPortal(
        "Trade Republic", "https://traderepublic.com/en-de/careers", 3, "BI and analytics"
    ),
    CareerPortal("Flix", "https://flix.careers/", 3, "Business intelligence"),
    CareerPortal("GetYourGuide", "https://careers.getyourguide.com/", 3, "Product analytics"),
    CareerPortal("Contentful", "https://www.contentful.com/careers/", 3, "Product data"),
    CareerPortal("SumUp", "https://careers.sumup.com/", 3, "Data analysis"),
    CareerPortal("Mytheresa", "https://career.mytheresa.com/", 3, "Business analytics"),
    CareerPortal(
        "Microsoft",
        "https://jobs.careers.microsoft.com/global/en/search",
        2,
        "Software, data and cloud support",
    ),
    CareerPortal("IBM", "https://www.ibm.com/careers/search", 2, "Data science, AI and software"),
    CareerPortal("Amazon", "https://www.amazon.jobs/en/search", 2, "BI, data, software and cloud"),
    CareerPortal(
        "Accenture",
        "https://www.accenture.com/de-en/careers",
        2,
        "Analytics, BI and software consulting",
    ),
    CareerPortal(
        "Capgemini", "https://www.capgemini.com/de-de/karriere/", 2, "Data, SQL, BI and software"
    ),
)
