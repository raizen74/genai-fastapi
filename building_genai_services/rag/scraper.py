import asyncio
import re

import aiohttp
from bs4 import BeautifulSoup
from loguru import logger


def extract_urls(text: str) -> list[str]:
    url_pattern = r"(?P<url>https?:\/\/[^\s]+)"
    urls = re.findall(url_pattern, text)
    return urls


def parse_inner_text(html_string: str) -> str:
    logger.info(f"{html_string = }")
    soup = BeautifulSoup(html_string, "lxml")
    if content := soup.find("div", id="bodyContent"):  # checking for id="bodyContent" can result in issues, review
        logger.info(f"{content.get_text() = }")
        return content.get_text()
    logger.warning("Could not parse the HTML content")
    return ""


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        html_string = await response.text()
        return parse_inner_text(html_string)


async def fetch_all(urls: list[str]) -> str:
    logger.info(f"{urls = }")
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            *[fetch(session, url) for url in urls], return_exceptions=True
        )
    success_results = [
        result for result in results if isinstance(result, str) and result.strip()
    ]
    if len(results) != len(success_results):
        logger.warning("Some URLs could not be fetched or returned no content")
    return " ".join(success_results)
