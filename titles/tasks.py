# titles/tasks.py
from jikanpy import Jikan
import jikanpy.exceptions
import time
from .models import Title
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def parser_queue():
    logger.info('Starting parser_queue')
    jikan = Jikan()

    def get_data(page: int):
        while True:
            try:
                data = jikan.top(type='anime', page=page)
                return data
            except jikanpy.exceptions.APIException:
                #logger.warning(f"API rate limit hit on page {page}, retrying in 1s")
                time.sleep(1)
            except Exception as e:
                logger.warning(f'{e=}')
                time.sleep(10)

    def animes_processing(animes: list[dict]):
        for anime in animes:
            shikimori_id = int(anime['mal_id'])
            title = anime['titles'][0]['title']
            year = anime['year']
            description = anime['synopsis']
            #logger.info(f'Adding anime {shikimori_id=}')
            try:
                Title.objects.update_or_create(
                    shikimori_id=shikimori_id,
                    defaults={"title": title, "year": year, "description": description},
                )
            except Exception as e:
                import json
                logger.info(json.dumps(anime, indent=4, ensure_ascii=False))
                raise e

    page = 1
    while True:
        try:
            logger.info(f'Processing {page=}')
            data = get_data(page)
            has_next_page = data['pagination']['has_next_page']
            animes = data['data']
            animes_processing(animes)
            if not has_next_page:
                logger.info("No more pages to process, task completed")
                break
            page += 1
        except Exception as e:
            logger.error(f"Error processing page {page}: {e}")
            break
