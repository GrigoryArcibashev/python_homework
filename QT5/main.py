import sys
import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTime, QTimer, QUrl
from PyQt5.QtMultimedia import QSoundEffect

from ui import UiMainWindow


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = UiMainWindow()
        self.ui.setup_ui(self)

        self._time = None
        self._pause_time = None
        self._timer = None
        self._setup_timer()
        self._setup_components()

    def _setup_components(self):
        self._assign_slots_to_components()
        self._hide_components(
                [self.ui.stop_btn, self.ui.pause_btn, self.ui.start_btn])

    def _assign_slots_to_components(self):
        self.ui.timer_editor.timeChanged.connect(self._edit_timer)
        self.ui.signal_selector.currentIndexChanged.connect(
            self._select_signal)
        self.ui.start_btn.clicked.connect(self._start)
        self.ui.pause_btn.clicked.connect(self._pause)
        self.ui.stop_btn.clicked.connect(self._stop)

    def _setup_timer(self):
        self._timer = QTimer()
        self._timer.timeout.connect(self._show_time)

    def _start(self):
        if self._time is None:
            self._time = self.ui.timer_editor.time()
            self.ui.timer_state.setText(self._time.toString('HH:mm:ss'))
        else:
            time.sleep(self._pause_time / 1000)
            self._pause_time = None
            self._show_time()
        self._timer.start(1000)
        self._hide_components(
                [self.ui.start_btn, self.ui.timer_editor,
                 self.ui.signal_selector])
        self._show_components([self.ui.pause_btn, self.ui.stop_btn])

    def _pause(self):
        self._pause_time = self._timer.remainingTime()
        self._timer.stop()
        self._hide_components([self.ui.pause_btn])
        self._show_components([self.ui.start_btn])

    def _stop(self):
        self._timer.stop()
        self._time = None
        self.ui.timer_state.setText('00:00:00')
        self._hide_components([self.ui.stop_btn, self.ui.pause_btn])
        self._show_components(
                [self.ui.start_btn, self.ui.timer_editor,
                 self.ui.signal_selector])

    def _edit_timer(self):
        if self._is_time_zero(self.ui.timer_editor.time()):
            self._hide_components([self.ui.start_btn])
        else:
            self._show_components([self.ui.start_btn])

    def _select_signal(self):
        if self.ui.signal_selector.currentText() != "Без звука":
            self._path_to_music_file = self._get_music_file_path()
            if not self._path_to_music_file:
                self.ui.signal_selector.setCurrentText("Без звука")

    def _signal(self):
        if self.ui.signal_selector.currentText() != "Без звука":
            snd = QSoundEffect()
            snd.setVolume(1)
            fn = QUrl.fromLocalFile(self._path_to_music_file)
            snd.setSource(fn)
            snd.setLoopCount(1)
            snd.play()

    def _show_time(self):
        self._time = self._reduce_time(self._time)
        self.ui.timer_state.setText(self._time.toString('HH:mm:ss'))
        if self._is_time_zero(self._time) or self._time.isNull():
            self._stop()
            self._signal()

    def _get_music_file_path(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self,
                "Select Audio File",
                "",
                "Audio File (*.mp3 *.wav *.ogg)",
                options=options)
        if not path:
            return None
        return path

    @staticmethod
    def _hide_components(components: list):
        for component in components:
            component.setEnabled(False)

    @staticmethod
    def _show_components(components: list):
        for component in components:
            component.setEnabled(True)

    @staticmethod
    def _is_time_zero(q_time: QTime):
        return q_time.hour() == q_time.minute() == q_time.second() == 0

    @staticmethod
    def _reduce_time(q_time: QTime) -> QTime:
        h = q_time.hour()
        m = q_time.minute()
        s = q_time.second()
        if s > 0:
            return QTime(h, m, s - 1)
        if m > 0:
            return QTime(h, m - 1, 59)
        if h > 0:
            return QTime(h - 1, 59, 59)
        return QTime()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    application = Window()
    application.show()
    sys.exit(app.exec())
