from ffmpeg import FFmpeg
from celery import shared_task
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import tempfile
from uploads.models import Video
from .choices import HSLStatus
from .serializers import HLSVideoSerializer
from .models import HLSVideo
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_video(video_id: int):
    try:
        video_model: Video = Video.objects.get(id=video_id)

        url = video_model.video_file.url
        url = url.replace('127.0.0.1', 'minio')
        hls_base_path = f'videos/hls/{video_model.uuid}'
        video_model.video_file
        results = []
        for resolution in [(1920, 1080), (1280, 720), (720, 480)]:
            width, height = resolution
            hls_serializer = HLSVideoSerializer(
                data={
                    'video':video_model.pk, 
                    'status':HSLStatus.PROCESSING, 
                    'width':width,
                    'height':height,
                }
            )
            hls_serializer.is_valid(raise_exception=True)
            hls:HLSVideo = hls_serializer.save()
            
            hls_path = f'{hls_base_path}/{hls.width}x{hls.height}/'
            hls_playlist_filename = 'index.m3u8'

            with tempfile.TemporaryDirectory() as temp_dir:
                output_file = os.path.join(temp_dir, hls_playlist_filename)

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
                                's': f'{width}x{height}',
                                'start_number': '0',
                                'hls_time': '10',
                                'hls_list_size': '0',
                                'hls_segment_type': 'mpegts'
                            }
                        )
                    )

                    ffmpeg.execute()

                    for file_name in os.listdir(temp_dir):
                        local_path = os.path.join(temp_dir, file_name)
                        minio_path = os.path.join(hls_path, file_name)
                        with open(local_path, 'rb') as file:
                            logger.info(f'Uploading to MinIO: {minio_path}')
                            saved_path = default_storage.save(minio_path, ContentFile(file.read()))
                            logger.info(f'Uploaded as: {saved_path}')

                    hls_playlist_url = default_storage.url(
                        os.path.join(hls_path, hls_playlist_filename)
                    )
                    logger.info(f'HLS playlist URL: {hls_playlist_url}')
                    
                    HLSVideo.objects.filter(pk=hls.pk).update(url=hls_playlist_url, status=HSLStatus.READY)
                    results.append(f"HLS {width}x{height} processed")

                except Exception as e:
                    HLSVideo.objects.filter(pk=hls.pk).update(status=HSLStatus.FAILED)
                    logger.error(f"FFmpeg failed for {width}x{height}: {str(e)}")
                    results.append(f"HLS {width}x{height} failed: {str(e)}")
                    continue

        return "\n".join(results)

    except Video.DoesNotExist:
        return f"Видео с ID {video_id} не найдено"
    except Exception as e:
        return f"Ошибка при обработке видео {video_id}: {str(e)}"