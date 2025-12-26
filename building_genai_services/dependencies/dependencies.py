from fastapi import Body
from loguru import logger

from building_genai_services.schemas import TextModelRequest
from building_genai_services.scraper import extract_urls, fetch_all


async def get_urls_content(body: TextModelRequest = Body(...)) -> str:
    urls = extract_urls(body.prompt)
    logger.info(f"{urls = }")
    if urls:
        try:
            urls_content = await fetch_all(urls)
            return urls_content
        except Exception as e:
            logger.warning(f"Failed to fetch one or several URls - Error: {e}")
    return ""
