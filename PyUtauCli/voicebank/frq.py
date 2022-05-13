'''frq

frq関係のデータを扱います。

'''

import os
import os.path
import struct

import numpy as np
import pyworld as pw
import PyRwu.wave_io

class Frq:
    '''
    frqファイルを扱います。
    
    Attributes
    ----------
    frqpath: str
        | frqファイルのパス

    framerate: int, default = 44100
        wavのサンプリング周波数

    f0: np.ndarray of np.float64
        f0データの1次元配列

    f0_avg: float
        平均キー

    amp: np.ndarray of np.float64
        音量データの1次元配列

    t: np.ndarray
        時間配列。原則として256sample毎に与えられる。
    '''

    frqpath: str
    framerate: int = 44100
    f0: np.ndarray
    amp: np.ndarray
    t: np.ndarray

    def __init__(self, frqpath: str = "", framerate: int = 44100):
        '''
        Parameters
        ----------
        frqpath: str, default = ""
            frqのパス。

        framerate: int, default 44100
            wavのサンプリング周波数

        Raises
        ------
        FileNotFoundError
            指定したfrqファイルが存在しないとき
        '''
        self.frqpath = frqpath
        self.framerate = framerate
        if frqpath != "":
            self.load(frqpath, framerate)

    def load(self, frqpath: str, framerate: int):
        '''
        frqpathで指定したファイルを開き、self.f0, self.f0_avg, self.amp, self.tを更新します。

        Parameters
        ----------
        frqpath: str
            frqのパス。

        framerate: int
            wavのサンプリング周波数

        Raises
        ------
        FileNotFoundError
            指定したfrqファイルが存在しないとき
        '''
        if not os.path.isfile(frqpath):
            raise FileNotFoundError("{} is not found.".format(frqpath))
        with open(frqpath, "rb") as fr:
            bytes_data = fr.read()
        self.f0_avg = struct.unpack("<d", bytes_data[12:20])[0]
        data: np.ndarray = np.frombuffer(bytes_data[40:], dtype="float64")
        self.f0 = data[::2]
        self.amp = data[1::2]
        frq_span = 1 / framerate * 256
        self.t = np.arange(0, frq_span * (self.f0.shape[0]+1), frq_span)[:self.f0.shape[0]]

    def save(self):
        '''
        self.frqpathで指定したパスにfrqファイルを保存します。
        '''
        with open(self.frqpath, "wb") as fw:
            fw.write(b"FREQ0003")
            fw.write((256).to_bytes(4,"little"))
            fw.write(np.array(self.f0_avg, dtype=np.float64).tobytes())
            fw.write(b"PyUtauCli       ")
            fw.write(self.f0.shape[0].to_bytes(4,"little"))
            fw.write(np.concatenate([[self.f0],[self.amp]]).T.tobytes())

    def make(self, wavpath: str):
        '''
        wavpathで指定したwavファイルを解析し、self.frqpath, self.framerate, self.f0, self.f0_avg, self.amp, self.tを更新します。

        Parameters
        ----------
        wavpath: str
            wavファイルの絶対パス

        Raises
        ------
        FileNotFoundError
            wavpathのwavファイルが見つからなかったとき
        TypeError
            input_pathで指定したファイルがwavではなかったとき
        '''
        datas, self.framerate = PyRwu.wave_io.read(wavpath, 0, 0)
        self.frqpath = ".".join(wavpath.split(".")[:-1])+"_wav.frq"
        self.f0, self.t = pw.harvest(datas, self.framerate, frame_period = 1000/ self.framerate * 256)
        self.f0 = pw.stonemask(datas, self.f0, self.t, self.framerate)
        self.amp = np.zeros_like(self.f0)
        for i in range(self.amp.shape[0]):
            self.amp[i] = np.average(np.abs(datas[i*256:(i+1)*256]))