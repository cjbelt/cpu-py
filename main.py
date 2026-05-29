import os
import sys
import multiprocessing

diretorio_raiz = os.path.abspath(os.path.dirname(__file__))

if diretorio_raiz not in sys.path:
    sys.path.insert(0, diretorio_raiz)

from src.ui.interface import MonitorApp

if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = MonitorApp()
    app.mainloop()
