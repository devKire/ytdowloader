import yt_dlp
import os
import threading
from typing import Callable, Dict, Any
import json

class YouTubeDownloader:
    def __init__(self):
        self.is_downloading = False
        self.current_progress = 0
        
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Obtém informações do vídeo"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Formatar informações
                video_info = {
                    'title': info.get('title', 'Desconhecido'),
                    'duration': self.format_duration(info.get('duration', 0)),
                    'uploader': info.get('uploader', 'Desconhecido'),
                    'view_count': f"{info.get('view_count', 0):,}",
                    'upload_date': self.format_date(info.get('upload_date', '')),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', 'Sem descrição'),
                    'formats': self.get_available_formats(info)
                }
                
                return video_info
                
        except Exception as e:
            raise Exception(f"Erro ao obter informações: {str(e)}")
    
    def get_available_formats(self, info: Dict) -> Dict[str, list]:
        """Obtém formatos disponíveis"""
        formats = {'video': [], 'audio': []}
        
        if 'formats' in info:
            for fmt in info['formats']:
                format_note = fmt.get('format_note', 'unknown')
                ext = fmt.get('ext', 'unknown')
                filesize = fmt.get('filesize', fmt.get('filesize_approx', 0))
                
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                    # Formato de vídeo com áudio
                    resolution = f"{format_note}" if format_note != 'none' else f"{fmt.get('height', '?')}p"
                    formats['video'].append({
                        'format_id': fmt['format_id'],
                        'resolution': resolution,
                        'ext': ext,
                        'filesize': self.format_filesize(filesize),
                        'quality': f"{resolution} ({ext})"
                    })
                elif fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                    # Apenas áudio
                    abr = fmt.get('abr', 0)
                    formats['audio'].append({
                        'format_id': fmt['format_id'],
                        'quality': f"{abr}kbps ({ext})",
                        'ext': ext,
                        'filesize': self.format_filesize(filesize)
                    })
        
        # Remover duplicatas e ordenar
        formats['video'] = self.remove_duplicate_formats(formats['video'])
        formats['audio'] = self.remove_duplicate_formats(formats['audio'])
        
        return formats
    
    def remove_duplicate_formats(self, formats: list) -> list:
        """Remove formatos duplicados"""
        seen = set()
        unique_formats = []
        
        for fmt in formats:
            identifier = (fmt['resolution'] if 'resolution' in fmt else fmt['quality'])
            if identifier not in seen:
                seen.add(identifier)
                unique_formats.append(fmt)
        
        return unique_formats
    
    def download_video(self, url: str, options: Dict, progress_callback: Callable = None) -> None:
        """Faz download do vídeo/áudio"""
        self.is_downloading = True
        
        ydl_opts = {
            'outtmpl': options.get('output_template', 'downloads/%(title)s.%(ext)s'),
            'progress_hooks': [progress_callback] if progress_callback else [],
            'quiet': False,
        }
        
        # Configurar formato
        if options['download_type'] == 'video':
            if options['video_quality'] == 'best':
                ydl_opts['format'] = 'best[height<=1080]'
            else:
                ydl_opts['format'] = options['video_quality']
        else:
            # Download de áudio
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': options.get('audio_format', 'mp3'),
                'preferredquality': options.get('audio_quality', '192'),
            }]
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
        except Exception as e:
            raise Exception(f"Erro no download: {str(e)}")
        finally:
            self.is_downloading = False
    
    def format_duration(self, seconds: int) -> str:
        """Formata duração em segundos para string"""
        if not seconds:
            return "Desconhecido"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def format_date(self, date_str: str) -> str:
        """Formata data YYYYMMDD para DD/MM/YYYY"""
        if len(date_str) == 8:
            return f"{date_str[6:8]}/{date_str[4:6]}/{date_str[0:4]}"
        return date_str
    
    def format_filesize(self, size_bytes: int) -> str:
        """Formata tamanho do arquivo"""
        if not size_bytes:
            return "Desconhecido"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"