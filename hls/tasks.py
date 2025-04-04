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
import subprocess
import json
from django.db.models.fields.files import FieldFile

logger = logging.getLogger(__name__)

@shared_task
def process_video(video_id: int):
    try:
        video_model: Video = Video.objects.get(id=video_id)

        video_file = video_model.video_file        
        assert isinstance(video_file, FieldFile)
        metadata = get_video_metadata(video_file)
        Video.objects.filter(pk=video_model.pk).update(**metadata)        
        #url = video_model.video_file.url
        #url = url.replace('127.0.0.1', 'minio')
        
        dash_base_path = f'videos/dash/{video_model.uuid}'
    
        hls_serializer = HLSVideoSerializer(
            data={
                'video':video_model.pk, 
                'status':HSLStatus.PROCESSING, 
            }
        )
        hls_serializer.is_valid(raise_exception=True)
        hls:HLSVideo = hls_serializer.save()
        
        source_video = video_file.name
        dash_init_segment = 'init_$RepresentationID$.$ext$'
        dash_media_segment = 'segment_$RepresentationID$_$Number$.$ext$'
        dash_manifest = 'stream.mpd'
        with tempfile.TemporaryDirectory() as temp_dir: 
            output_file = os.path.join(temp_dir, dash_manifest)
            try:
                ffmpeg = (
                    FFmpeg()
                    .input(source_video)
                    .output(
                        output_file,
                        {
                            # Video processing using filter_complex for multiple resolutions
                            "filter_complex": (
                                "[0:v]scale=-2:144[v144];"
                                "[0:v]scale=-2:480[v480];"
                                "[0:v]scale=-2:1080[v1080]"
                            ),
                            # Map all streams
                            #"map": ["[v144]", "[v480]", "[v1080]", "0:a?", "0:s?"],
                            "map": ["[v144]", "[v480]", "[v1080]", "0:a"],
                            # Video codec settings
                            'c:v': 'libx264',
                            "b:v:0": "600k",  # Bitrate for 144p
                            "b:v:1": "1500k",  # Bitrate for 480p
                            "b:v:2": "6000k",  # Bitrate for 1080p
                            # Настройки аудио
                            'c:a': 'aac', 
                            'b:a': '128k',
                            "disposition:a": "default",
                            "map_metadata:s:a": "0:s:a",
                            # Настройки субтитров
                            'c:s': 'webvtt',
                            # Настройки DASH
                            'map_metadata': '0',
                            'f': 'dash',
                            'use_timeline': '1',
                            'use_template': '1',
                            'seg_duration': '3',
                            #'adaptation_sets': "id=0,streams=v id=1,streams=a id=2,streams=s",
                            'adaptation_sets': "id=0,streams=v id=1,streams=a",
                            'init_seg_name': dash_init_segment,
                            'media_seg_name': dash_media_segment,
                            'y': None,
                        }
                    )
                )
                logger.info(' '.join(ffmpeg.arguments))
                ffmpeg.execute()
                for file_name in os.listdir(temp_dir):
                    local_path = os.path.join(temp_dir, file_name)
                    minio_path = os.path.join(dash_base_path, file_name)
                    with open(local_path, 'rb') as file:
                        #logger.info(f'Uploading to MinIO: {minio_path}')
                        saved_path = default_storage.save(minio_path, ContentFile(file.read()))
                        #logger.info(f'Uploaded as: {saved_path}')
                
                hls_playlist_url = default_storage.url(
                    os.path.join(dash_base_path, dash_manifest)
                )
                logger.info(f'HLS playlist URL: {hls_playlist_url}')
                
                HLSVideo.objects.filter(pk=hls.pk).update(url=hls_playlist_url, status=HSLStatus.READY)

            except Exception as e:
                HLSVideo.objects.filter(pk=hls.pk).update(status=HSLStatus.FAILED)
                process = subprocess.run(ffmpeg.arguments, capture_output=True, text=True)
                logger.error(f'FFmpeg stdout: {process.stdout}')
                logger.error(f'FFmpeg stderr: {process.stderr}')
                raise e

        return True

    except Video.DoesNotExist:
        return f"Видео с ID {video_id} не найдено"
    except Exception as e:
        return f"Ошибка при обработке видео {video_id}: {str(e)}"

def get_video_metadata(video_file:FieldFile) -> dict:
    """
    Получает метаданные видео с использованием ffprobe.
    """
    try:
        file_path_to_process = video_file.name
        logger.info(f'{file_path_to_process=}')
        if not os.path.exists(file_path_to_process):
            raise FileNotFoundError(f"Video file not found: {file_path_to_process}")
        
        ffprobe_cmd = [
            'ffprobe',
            '-v', 'error',           # Уровень логирования
            '-show_streams',         # Показать информацию о потоках
            '-show_format',          # Показать информацию о формате
            '-print_format', 'json', # Вывод в JSON
            file_path_to_process     # Путь к файлу
        ]
        
        result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
        metadata_json = json.loads(result.stdout)
        video_stream = next((stream for stream in metadata_json['streams'] if stream['codec_type'] == 'video'), None)
        audio_stream = next((stream for stream in metadata_json['streams'] if stream['codec_type'] == 'audio'), None)

        if not video_stream:
            raise ValueError("No video stream found")

        metadata = {
            # Основные метаданные
            'size': int(metadata_json['format']['size']),
            'duration': int(float(metadata_json['format']['duration'])),
            'width': int(video_stream['width']),
            'height': int(video_stream['height']),
            'bitrate': int(metadata_json['format'].get('bit_rate', video_stream.get('bit_rate', 0))),
            # Дополнительные метаданные видео
            'frame_rate': video_stream['r_frame_rate'],
            'codec': video_stream['codec_name'],
            'frame_count': int(video_stream.get('nb_frames', 0)) if video_stream.get('nb_frames') else None,
            # Аудио метаданные
            'audio_codec': audio_stream['codec_name'] if audio_stream else None,
            'sample_rate': int(audio_stream['sample_rate']) if audio_stream else None,
            'channels': int(audio_stream['channels']) if audio_stream else None,
            'audio_bitrate': int(audio_stream.get('bit_rate', 0)) if audio_stream else None,
        }
        return metadata

    except subprocess.CalledProcessError as e:
        raise Exception(f"FFprobe error: {e.stderr}")
    except Exception as e:
        raise Exception(f"Error processing video metadata: {str(e)}")