import tkinter as tk
from .gui import YouTubeDownloaderGUI
import sys
import os

def main():
    # Adicionar o diretório src ao path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    try:
        root = tk.Tk()
        app = YouTubeDownloaderGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {e}")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()