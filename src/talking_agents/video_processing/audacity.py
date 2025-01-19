from typeguard import typechecked
from pathlib import Path
import time
import logging
import subprocess
import pyaudacity as pa
import tempfile

log = logging.getLogger(__name__)


class AudacityInstance:
    def __init__(self, instance: subprocess.Popen):
        self._instance = instance

    def close(self):
        with tempfile.TemporaryDirectory() as dir:
            self.do(f"SaveProject2: Filename={Path(dir) / 'project.aup3'}")
            time.sleep(10)

            # Unfortunately audacity crashes when we close or exist the project
            #  in this case the python script is hanging forever, because it cannot communicate with
            #  audacity anymore. To prevent this, we just terminate the process.
            #self.do("Exit")
            #time.sleep(10)

            self._instance.terminate()
            time.sleep(10)


    @typechecked()
    def do(self, command: str):
        log.info("Process audacity command: %s", command)
        pa.do(command)

    @typechecked()
    def open_file(self, file_name: Path):
        file_name = file_name.absolute()
        self.do(f"Import2: Filename={file_name}")

    @typechecked()
    def export_wave(self, file_name: Path):
        file_name = file_name.absolute()
        self.do(f"Export2: Filename={file_name}")

    @typechecked()
    def apply_macro(self, macro_name: str):
        self.do(f"Macro_{macro_name}")


class Audacity:
    @typechecked()
    def __init__(self, tool_path: Path):
        self._tool_path = tool_path
        self._instance = None

    def __enter__(self) -> AudacityInstance:
        if self._instance is None:
            self._instance = AudacityInstance(self._create_instance())
        return self._instance

    def __exit__(self, type, value, traceback):
        self._instance.close()
        self._instance = None

    @typechecked()
    def _create_instance(self) -> subprocess.Popen:
        log.info("Create Audacity instance ...")
        instance = subprocess.Popen([self._tool_path])
        time.sleep(10)
        return instance
