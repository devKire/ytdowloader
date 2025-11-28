import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
from PIL import Image, ImageTk
import requests
from io import BytesIO
from .downloader import YouTubeDownloader

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader Pro")
        self.root.geometry("800x700")
        self.root.configure(bg='#2b2b2b')
        
        self.downloader = YouTubeDownloader()
        self.current_thumbnail = None
        
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        """Configura os estilos da interface"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar cores
        self.style.configure('TFrame', background='#2b2b2b')
        self.style.configure('TLabel', background='#2b2b2b', foreground='white')
        self.style.configure('TButton', background='#404040', foreground='white')
        self.style.configure('TRadiobutton', background='#2b2b2b', foreground='white')
        self.style.configure('TCheckbutton', background='#2b2b2b', foreground='white')
        self.style.configure('TEntry', fieldbackground='#404040', foreground='white')
        self.style.configure('TCombobox', fieldbackground='#404040', foreground='white')
        self.style.configure('TProgressbar', background='#00ff00', troughcolor='#404040')
        
    def create_widgets(self):
        """Cria os widgets da interface"""
            # === SCROLL MASTER ===
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg="#2b2b2b", highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)

        # Frame interno que vai receber TODOS os widgets
        main_frame = ttk.Frame(canvas, padding="10")
        window_id = canvas.create_window((0, 0), window=main_frame, anchor="n")

        def resize_frame(event):
            canvas.itemconfig(window_id, width=event.width)

        canvas.bind("<Configure>", resize_frame)


        # Atualizar área scrollável quando mudar tamanho
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        main_frame.bind("<Configure>", on_configure)

        # Permitir rolagem com mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        
        # Título
        title_label = ttk.Label(main_frame, text="YouTube Downloader Pro", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Frame de entrada de URL
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(url_frame, text="URL do YouTube:").pack(anchor=tk.W)
        
        url_input_frame = ttk.Frame(url_frame)
        url_input_frame.pack(fill=tk.X, pady=5)
        
        self.url_entry = ttk.Entry(url_input_frame, font=('Arial', 10))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.fetch_btn = ttk.Button(url_input_frame, text="Buscar Informações", 
                                   command=self.fetch_video_info)
        self.fetch_btn.pack(side=tk.RIGHT)
        
        # Frame de informações do vídeo
        self.info_frame = ttk.LabelFrame(main_frame, text="Informações do Vídeo", padding="10")
        self.info_frame.pack(fill=tk.X, pady=10)
        
        # Thumbnail e informações básicas
        info_content_frame = ttk.Frame(self.info_frame)
        info_content_frame.pack(fill=tk.X)
        
        # Thumbnail
        self.thumbnail_label = ttk.Label(info_content_frame)
        self.thumbnail_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Informações textuais
        text_info_frame = ttk.Frame(info_content_frame)
        text_info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.title_label = ttk.Label(text_info_frame, text="Título: ", font=('Arial', 10, 'bold'))
        self.title_label.pack(anchor=tk.W)
        
        self.duration_label = ttk.Label(text_info_frame, text="Duração: ")
        self.duration_label.pack(anchor=tk.W)
        
        self.uploader_label = ttk.Label(text_info_frame, text="Canal: ")
        self.uploader_label.pack(anchor=tk.W)
        
        self.views_label = ttk.Label(text_info_frame, text="Visualizações: ")
        self.views_label.pack(anchor=tk.W)
        
        # Descrição
        ttk.Label(self.info_frame, text="Descrição:").pack(anchor=tk.W, pady=(10, 0))
        self.desc_text = scrolledtext.ScrolledText(self.info_frame, height=4, 
                                                  bg='#404040', fg='white', 
                                                  insertbackground='white')
        self.desc_text.pack(fill=tk.X, pady=5)
        
        # Frame de configurações de download
        self.download_frame = ttk.LabelFrame(main_frame, text="Configurações de Download", padding="10")
        self.download_frame.pack(fill=tk.X, pady=10)
        
        # Tipo de download
        download_type_frame = ttk.Frame(self.download_frame)
        download_type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(download_type_frame, text="Tipo:").pack(side=tk.LEFT)
        
        self.download_type = tk.StringVar(value="video")
        ttk.Radiobutton(download_type_frame, text="Vídeo", 
                       variable=self.download_type, value="video",
                       command=self.on_download_type_change).pack(side=tk.LEFT, padx=(20, 10))
        ttk.Radiobutton(download_type_frame, text="Áudio", 
                       variable=self.download_type, value="audio",
                       command=self.on_download_type_change).pack(side=tk.LEFT)
        
        # Qualidade do vídeo
        self.video_quality_frame = ttk.Frame(self.download_frame)
        self.video_quality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.video_quality_frame, text="Qualidade do Vídeo:").pack(side=tk.LEFT)
        
        self.video_quality = ttk.Combobox(self.video_quality_frame, state="readonly", width=30)
        self.video_quality.pack(side=tk.LEFT, padx=(10, 0))
        
        # Configurações de áudio
        self.audio_settings_frame = ttk.Frame(self.download_frame)
        
        audio_quality_frame = ttk.Frame(self.audio_settings_frame)
        audio_quality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(audio_quality_frame, text="Qualidade do Áudio:").pack(side=tk.LEFT)
        
        self.audio_quality = ttk.Combobox(audio_quality_frame, state="readonly", width=20)
        self.audio_quality.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(audio_quality_frame, text="Formato:").pack(side=tk.LEFT, padx=(20, 0))
        
        self.audio_format = ttk.Combobox(audio_quality_frame, 
                                        values=['mp3', 'm4a', 'wav', 'ogg'], 
                                        state="readonly", width=10)
        self.audio_format.set('mp3')
        self.audio_format.pack(side=tk.LEFT, padx=(10, 0))
        
        # Local de download
        location_frame = ttk.Frame(self.download_frame)
        location_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(location_frame, text="Local de Download:").pack(side=tk.LEFT)
        
        self.location_entry = ttk.Entry(location_frame, width=50)
        self.location_entry.insert(0, os.path.join(os.getcwd(), 'downloads'))
        self.location_entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)
        
        ttk.Button(location_frame, text="Procurar", 
                  command=self.browse_download_location).pack(side=tk.LEFT)
        
        # Botão de download
        self.download_btn = ttk.Button(main_frame, text="Iniciar Download", 
                                      command=self.start_download, state='disabled')
        self.download_btn.pack(pady=20)
        
        # Barra de progresso
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X)
        
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack()
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=False, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, bg='#404040', fg='white',
                                                 insertbackground='white')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Inicialmente esconder frames
        self.info_frame.pack_forget()
        self.download_frame.pack_forget()
        self.progress_frame.pack_forget()
        
    def fetch_video_info(self):
        """Busca informações do vídeo"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Erro", "Por favor, insira uma URL do YouTube")
            return
        
        self.log("Buscando informações do vídeo...")
        self.fetch_btn.config(state='disabled')
        
        # Executar em thread separada
        thread = threading.Thread(target=self._fetch_video_info_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def _fetch_video_info_thread(self, url):
        """Thread para buscar informações do vídeo"""
        try:
            video_info = self.downloader.get_video_info(url)
            self.root.after(0, self._on_video_info_fetched, video_info)
        except Exception as e:
            self.root.after(0, self._on_video_info_error, str(e))
    
    def _on_video_info_fetched(self, video_info):
        """Callback quando as informações são obtidas"""
        self.video_info = video_info
        self.fetch_btn.config(state='normal')
        
        # Atualizar interface com informações
        self.title_label.config(text=f"Título: {video_info['title']}")
        self.duration_label.config(text=f"Duração: {video_info['duration']}")
        self.uploader_label.config(text=f"Canal: {video_info['uploader']}")
        self.views_label.config(text=f"Visualizações: {video_info['view_count']}")
        
        # Limpar e inserir descrição
        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(1.0, video_info['description'])
        
        # Carregar thumbnail
        self.load_thumbnail(video_info['thumbnail'])
        
        # Configurar qualidades disponíveis
        self.setup_quality_options(video_info['formats'])
        
        # Mostrar frames
        self.info_frame.pack(fill=tk.X, pady=10)
        self.download_frame.pack(fill=tk.X, pady=10)
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.download_btn.config(state='normal')
        self.log("Informações do vídeo carregadas com sucesso!")
    
    def _on_video_info_error(self, error_msg):
        """Callback em caso de erro"""
        self.fetch_btn.config(state='normal')
        messagebox.showerror("Erro", error_msg)
        self.log(f"Erro: {error_msg}")
    
    def load_thumbnail(self, thumbnail_url):
        """Carrega a thumbnail do vídeo"""
        try:
            response = requests.get(thumbnail_url, timeout=10)
            image = Image.open(BytesIO(response.content))
            image.thumbnail((160, 120), Image.Resampling.LANCZOS)
            self.current_thumbnail = ImageTk.PhotoImage(image)
            self.thumbnail_label.config(image=self.current_thumbnail)
        except Exception as e:
            self.log(f"Erro ao carregar thumbnail: {str(e)}")
    
    def setup_quality_options(self, formats):
        """Configura as opções de qualidade"""
        # Vídeo
        video_qualities = [fmt['quality'] for fmt in formats['video']]
        self.video_quality['values'] = video_qualities
        if video_qualities:
            self.video_quality.set(video_qualities[0])
        
        # Áudio
        audio_qualities = [fmt['quality'] for fmt in formats['audio']]
        self.audio_quality['values'] = audio_qualities
        if audio_qualities:
            self.audio_quality.set(audio_qualities[0])
    
    def on_download_type_change(self):
        """Altera a interface baseada no tipo de download"""
        if self.download_type.get() == 'video':
            self.video_quality_frame.pack(fill=tk.X, pady=5)
            self.audio_settings_frame.pack_forget()
        else:
            self.video_quality_frame.pack_forget()
            self.audio_settings_frame.pack(fill=tk.X, pady=5)
    
    def browse_download_location(self):
        """Abre diálogo para escolher local de download"""
        directory = filedialog.askdirectory()
        if directory:
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, directory)
    
    def start_download(self):
        """Inicia o download"""
        if not hasattr(self, 'video_info'):
            messagebox.showerror("Erro", "Por favor, busque as informações do vídeo primeiro")
            return
        
        # Configurar opções
        download_options = {
            'download_type': self.download_type.get(),
            'output_template': os.path.join(self.location_entry.get(), '%(title)s.%(ext)s'),
        }
        
        if self.download_type.get() == 'video':
            # Obter format_id da qualidade selecionada
            selected_quality = self.video_quality.get()
            for fmt in self.video_info['formats']['video']:
                if fmt['quality'] == selected_quality:
                    download_options['video_quality'] = fmt['format_id']
                    break
        else:
            download_options['audio_format'] = self.audio_format.get()
            # Extrair qualidade do áudio (ex: "128kbps" -> "128")
            selected_audio = self.audio_quality.get()
            quality_value = selected_audio.split('kbps')[0].strip()
            download_options['audio_quality'] = quality_value
        
        self.log("Iniciando download...")
        self.download_btn.config(state='disabled')
        self.progress_bar['value'] = 0
        
        # Executar download em thread separada
        thread = threading.Thread(target=self._download_thread, 
                                 args=(self.url_entry.get(), download_options))
        thread.daemon = True
        thread.start()
    
    def _download_thread(self, url, options):
        """Thread para download"""
        def progress_hook(d):
            if d['status'] == 'downloading':
                if 'total_bytes' in d and d['total_bytes']:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    self.root.after(0, self._update_progress, percent, 
                                  f"Baixando: {percent:.1f}%")
                elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                    percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                    self.root.after(0, self._update_progress, percent, 
                                  f"Baixando (estimado): {percent:.1f}%")
            elif d['status'] == 'finished':
                self.root.after(0, self._download_finished, "Download concluído com sucesso!")
        
        try:
            self.downloader.download_video(url, options, progress_hook)
        except Exception as e:
            self.root.after(0, self._download_error, str(e))
    
    def _update_progress(self, value, text):
        """Atualiza barra de progresso"""
        self.progress_bar['value'] = value
        self.progress_label.config(text=text)
    
    def _download_finished(self, message):
        """Callback quando download é concluído"""
        self.progress_bar['value'] = 100
        self.progress_label.config(text=message)
        self.download_btn.config(state='normal')
        self.log(message)
        messagebox.showinfo("Sucesso", message)
    
    def _download_error(self, error_msg):
        """Callback em caso de erro no download"""
        self.download_btn.config(state='normal')
        self.progress_label.config(text="Erro no download")
        self.log(f"Erro no download: {error_msg}")
        messagebox.showerror("Erro", f"Falha no download: {error_msg}")
    
    def log(self, message):
        """Adiciona mensagem ao log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()