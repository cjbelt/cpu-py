import os
import sys

diretorio_raiz = os.path.abspath(os.path.dirname(__file__))
diretorio_info = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "info"))

if diretorio_raiz not in sys.path:
    sys.path.insert(0, diretorio_raiz)

if diretorio_info not in sys.path:
    sys.path.insert(0, diretorio_info)

from src.ui.interface import MonitorApp

if __name__ == '__main__':
    app = MonitorApp()
    app.mainloop()
