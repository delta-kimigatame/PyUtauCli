import os
import os.path
import shutil
from logging import Logger

import numpy as np
import PyRwu
import PyWavTool

from .Ust import Ust
from .RenderNote import RenderNote
from voicebank import VoiceBank
import settings.logger as mylogger
import settings

default_logger = mylogger.get_logger(__name__, False)

class FastResamp(PyRwu.Resamp):
    def _getAp(self,
               f0_floor: float,
               f0_ceil: float,
               frame_period: float,
               threshold: float):
        self._ap = np.zeros_like(self._sp)

class Render:
    '''
    ustからwavを生成する処理を扱います。
    '''
    _cache_dir: str
    _output_file: str
    _ust: Ust
    notes: list
    vb: VoiceBank

    def __init__(self, ust: Ust, *, voice_dir: str = "",cache_dir: str = "", output_file: str = "", logger: Logger = None):
        '''
        Parameters
        ----------
        ust: Ust
            load済みのustもしくはUtauPlugin形式のデータ

        voice_dir: str, default ""
            | ustで指定している音源以外で出力する場合に音源のフルパスを指定します。
            | %VOICE%はsettings.VOICE_ROOTの値に置き換えられます。

        cache_dir: str, default ""
            ustで指定している以外の場所にキャッシュファイルを生成する場合、フルパスを指定します。

        output_file: str, default ""
            ustで指定している以外の場所にwavファイルを生成する場合、フルパスを指定します。

        '''
        self.logger = logger or default_logger
        self._ust = ust
        self.notes = []
        
        self.vb = VoiceBank(self._init_voicedir(voice_dir))

        if cache_dir != "":
            self._cache_dir = cache_dir
        else:
            self._cache_dir = ust.cache_dir

        if output_file != "":
            self._output_file = output_file
        else:
            self._output_file = ust.output_file

        for note in ust.notes:
            note.apply_oto(self.vb.oto,self.vb.prefix)

        for note in ust.notes:
            self.notes.append(RenderNote(note, self.vb, self._cache_dir, self._output_file, ust.mode2))

    def _init_voicedir(self, voice_dir) -> str:
        '''
        voice_dirにsettingsの値を適用させ、正しいフルパスを返します。

        Parameters
        ----------
        voice_dir: str, default ""
            ustで指定している音源以外で出力する場合に音源のフルパスを指定します。

        Raises
        ------
        FileNotFoundError
            %VOICE%をsetting.VOICE_ROOTに置き換えたとき、指定したパスのUTAU音源フォルダが見つからなかったとき。

        '''
        if voice_dir == "":
            voice_dir = self._ust.voice_dir
        for root_dir in settings.VOICE_ROOT:
            if VoiceBank.is_utau_voicebank(os.path.join(root_dir,voice_dir.replace("%VOICE%",""))):
                voice_dir = os.path.join(root_dir, voice_dir.replace("%VOICE%",""))
                break
        else:
            self.logger.error("{} is not found or not utau vb.".format(voice_dir))
            raise FileNotFoundError("{} is not found or not utau vb.".format(voice_dir))

        return voice_dir

    def resamp(self, * , force:bool = False):
        '''
        PyRwu.Resampを使用してキャッシュファイルを生成する。

        Parameters
        ----------
        force: bool, default False
            Trueの場合、キャッシュファイルがあっても生成する。
        '''
        os.makedirs(self._cache_dir, exist_ok=True)
        for note in self.notes:
            if not note.require_resamp:
                continue
            if force or not os.path.isfile(note.cache_path):
                self.logger.info("{} {} {} {} {} {} {} {} {} {} {} {} {}".format(note.input_path, note.cache_path, note.target_tone, note.velocity, note.flags,
                                      note.offset, note.target_ms, note.fixed_ms, note.end_ms, note.intensity,
                                      note.modulation, note.tempo, note.pitchbend))
                resamp = PyRwu.Resamp(note.input_path, note.cache_path, note.target_tone, note.velocity, note.flags,
                                      note.offset, note.target_ms, note.fixed_ms, note.end_ms, note.intensity,
                                      note.modulation, note.tempo, note.pitchbend, logger=self.logger)
                resamp.resamp()
            else:
                self.logger.info("{} have be cached".format(note.cache_path))

                

    def fast_resamp(self, * , force:bool = False):
        '''
        FastResampを使用してキャッシュファイルを生成する。

        Parameters
        ----------
        force: bool, default False
            Trueの場合、キャッシュファイルがあっても生成する。
        '''
        os.makedirs(self._cache_dir, exist_ok=True)
        for note in self.notes:
            if not note.require_resamp:
                continue
            if force or not os.path.isfile(note.cache_path):
                self.logger.info("{} {} {} {} {} {} {} {} {} {} {} {} {}".format(note.input_path, note.cache_path, note.target_tone, note.velocity, note.flags,
                                      note.offset, note.target_ms, note.fixed_ms, note.end_ms, note.intensity,
                                      note.modulation, note.tempo, note.pitchbend))
                resamp = FastResamp(note.input_path, note.cache_path, note.target_tone, note.velocity, note.flags,
                                      note.offset, note.target_ms, note.fixed_ms, note.end_ms, note.intensity,
                                      note.modulation, note.tempo, note.pitchbend, logger=self.logger)
                resamp.resamp()
            else:
                self.logger.info("{} have be cached".format(note.cache_path))

    def append(self):
        '''
        PyWavToolを使用してキャッシュファイルから出力ファイルを合成する。
        '''
        output_dir: str = os.path.split(self._output_file)[0]
        if output_dir != "":
            os.makedirs(output_dir, exists_ok=True)

        if os.path.isfile(self._output_file+".whd"):
            os.remove(self._output_file+".whd")

        if os.path.isfile(self._output_file+".dat"):
            os.remove(self._output_file+".dat")
        wavtool = PyWavTool.WavTool(self._output_file)
        for note in self.notes:
            if note.direct:
                self.logger.info("{} {} {} {}".format(note.input_path, note.envelope, note.stp+note.offset, note.output_ms))
                wavtool.inputCheck(note.input_path)
                wavtool.setEnvelope([float(item) for item in note.envelope.split(" ")])
                wavtool.applyData(note.stp + note.offset, note.output_ms)
            else:
                self.logger.info("{} {} {} {}".format(note.cache_path, note.envelope, note.stp, note.output_ms))
                wavtool.inputCheck(note.cache_path)
                wavtool.setEnvelope([float(item) for item in note.envelope.split(" ")])
                wavtool.applyData(note.stp, note.output_ms)
        wavtool.write()
            
        with open(self._output_file, "wb") as fw:
            with open(self._output_file+".whd", "rb") as fr:
                fw.write(fr.read())
            with open(self._output_file+".dat", "rb") as fr:
                fw.write(fr.read())

        if os.path.isfile(self._output_file+".whd"):
            os.remove(self._output_file+".whd")

        if os.path.isfile(self._output_file+".dat"):
            os.remove(self._output_file+".dat")

    def clean(self):
        '''
        self._cache_dirとself._output_fileが存在すれば削除する。
        '''
        if os.path.isdir(self._cache_dir):
            shutil.rmtree(self._cache_dir)
        if os.path.isfile(self._output_file):
            os.remove(self._output_file)