import os

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer

from .config import log

SOUND_DIR = os.path.dirname(os.path.abspath(__file__))

FILES = {
    "pop": "Pop_app.mp3",
    "download": "Download.mp3",
    "done": "Downloaded.mp3",
    "error": "Error.mp3",
}

VOLUME = 0.7

_players = {}
_enabled = True


def set_enabled(value):
    global _enabled
    _enabled = bool(value)


def is_enabled():
    return _enabled


def _player(name):
    entry = _players.get(name)
    if entry is not None:
        return entry

    path = os.path.join(SOUND_DIR, FILES.get(name, ""))
    if not FILES.get(name) or not os.path.isfile(path):
        log.warning("Ses dosyasi bulunamadi: %s", path)
        _players[name] = None
        return None

    player = QMediaPlayer()
    output = QAudioOutput()
    output.setVolume(VOLUME)
    player.setAudioOutput(output)
    player.setSource(QUrl.fromLocalFile(path))
    _players[name] = (player, output)
    return _players[name]


def play(name):
    if not _enabled:
        return
    try:
        entry = _player(name)
        if entry is None:
            return
        player, _output = entry
        player.stop()
        player.setPosition(0)
        player.play()
    except Exception as exc:
        log.warning("Ses calinamadi (%s): %s", name, exc)


def shutdown():
    for entry in _players.values():
        if entry:
            try:
                entry[0].stop()
            except RuntimeError:
                pass
    _players.clear()
