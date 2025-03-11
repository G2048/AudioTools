import logging

import numpy as np
import pydub
from ffmpy import FFmpeg
from gradio import processing_utils

logger = logging.getLogger("stdout")


class AudioFile:
    __slot__ = ("list_audio", "name", "path", "output_path")

    def __init__(self, file_path: str, output_path: str = "."):
        # name without extension
        self.path = file_path
        self.name = os.path.basename(file_path).split(".")[0]
        self.list_audio = {}
        self.output_path = output_path

    @classmethod
    def create_from_numpy(cls, audio: np.ndarray):
        return

    def create(self, format: str) -> dict:
        self.list_audio.update({self.new_path(format): None})
        return self.list_audio

    def new_path(self, format: str):
        return os.path.join(self.output_path, f"{self.name}.{format}")

    # @classmethod
    def clean(self):
        self.list_audio.clear()


class AudioConverter:
    def __init__(self, file: AudioFile):
        self.file = file
        # self.file = output_file
        # self.file_path = file_path

    def convert_mp3(self):
        self.convert()

    def convert_ogg(self):
        self.convert("ogg")

    def convert_wav(self):
        self.convert("wav")

    # TODO: add capture of stderr !
    def convert(self, format="mp3"):
        logger.info(f"Converting {self.file.name} to {format}")
        ff = FFmpeg(inputs={self.file.path: None}, outputs=self.file.create(format))

        logger.debug(f"String for execution: {ff.cmd}")
        try:
            ff.run()
            logger.error(f"Error while converting {self.file} to {format}")
        except Exception as e:
            logger.error(e)
            logger.error(f"Error while converting {self.file} to {format}")
            logger.error(f"String for execution: {ff.cmd}")

    @staticmethod
    def to_numpy(file: str) -> np.ndarray:
        return processing_utils.audio_from_file(file)

    @staticmethod
    def to_format(audio: np.ndarray):
        # pydub.AudioSegment.from_mp3()
        segment = pydub.AudioSegment.from_file(file, format)
        np_array = np.array(segment.get_array_of_samples())
        if segment.channels > 1:
            np_array = np.mean(np_array, axis=1)
        return segment.frame_rate, np_array
