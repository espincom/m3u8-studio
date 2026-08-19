from PyQt6.QtCore import QObject, pyqtSignal
from .i18n import tr


class Task(QObject):
    changed = pyqtSignal()

    def __init__(self, url, name, out_dir):
        super().__init__()
        self.url = url
        self.name = name
        self.out_dir = out_dir
        self.status = "queued"
        self.progress = 0.0
        self.detail_key = "st_queued"
        self.detail_args = ()
        self.detail_raw = None
        self.quality = ""
        self.result_path = ""
        self.worker = None
        self.item = None
        self.widget = None

    def set_detail(self, key, *args):
        self.detail_key, self.detail_args, self.detail_raw = key, args, None

    def set_detail_raw(self, text):
        self.detail_raw = text

    def detail_text(self):
        if self.detail_raw is not None:
            return self.detail_raw
        return tr(self.detail_key, *self.detail_args)
