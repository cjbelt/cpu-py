import os
import sys

diretorio_raiz = os.path.abspath(os.path.dirname(__file__))

if diretorio_raiz not in sys.path:
    sys.path.insert(0, diretorio_raiz)

from src.ui.interface import MonitorApp

if __name__ == '__main__':
    app = MonitorApp()
    app.mainloop()
