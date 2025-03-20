from ffmpeg import FFmpeg
from celery import shared_task
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import tempfile
from uploads.models import Video
from .choices import VideoStatus
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_video(video_id: int):
    try:
        video_model = Video.objects.get(id=video_id)
        video_model.status = VideoStatus.PROCESSING
        video_model.save()

        url = video_model.video.url
        url = url.replace('127.0.0.1', 'minio')
        logger.info(f"Input URL: {url}")
        
        hls_base_path = f'videos/hls/{video_model.uuid}/'
        hls_playlist_filename = 'index.m3u8'

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, hls_playlist_filename)
            logger.info(f"Output file path: {output_file}")

            try:
                ffmpeg = (
                    FFmpeg()
                    .option('loglevel', 'info')
                    .option('y')
                    .input(url)
                    .output(
                        output_file,
                        {'f': 'hls'},
                        **{
                            'c:v': 'libx264',
                            'profile:v': 'main',
                            'level': '3.1',
                            's': '1280x720',
                            'start_number': '0',
                            'hls_time': '10',
                            'hls_list_size': '0',
                            'hls_segment_type': 'mpegts'
                        }
                    )
                )

                logger.info(f'FFmpeg command: {" ".join(ffmpeg.arguments)}')
                ffmpeg.execute()

                for file_name in os.listdir(temp_dir):
                    local_path = os.path.join(temp_dir, file_name)
                    minio_path = os.path.join(hls_base_path, file_name)
                    with open(local_path, 'rb') as file:
                        logger.info(f'Uploading to MinIO: {minio_path}')
                        saved_path = default_storage.save(minio_path, ContentFile(file.read()))
                        logger.info(f'Uploaded as: {saved_path}')

                hls_playlist_url = default_storage.url(
                    os.path.join(hls_base_path, hls_playlist_filename)
                )
                logger.info(f'HLS playlist URL: {hls_playlist_url}')
                
                video_model.hls_playlist = hls_playlist_url
                video_model.status = VideoStatus.READY
                video_model.save()

            except Exception as e:
                video_model.status = VideoStatus.FAILED
                video_model.save()
                logger.error(f"FFmpeg failed: {str(e)}")
                raise e

        return f"Конвертация завершена. HLS файлы загружены в MinIO по пути: {hls_base_path}"

    except Video.DoesNotExist:
        return f"Видео с ID {video_id} не найдено"
    except Exception as e:
        return f"Ошибка при обработке видео {video_id}: {str(e)}"