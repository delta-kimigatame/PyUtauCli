import os.path
import hashlib

from typing import Tuple

import numpy as np
import PyRwu.pitch

from .Note import Note
from voicebank import VoiceBank
import settings

class RenderNote:
    '''
    UTAUのNoteをresamplerやwavtoolに渡せるパラメータにしたもの。

    Attributes
    ----------
    input_path: str
        入力する原音のフルパス。

    cache_path: str
        resampが出力する中間ファイルのパス

    output_path: str
        wavtoolが出力する最終ファイルのパス

    target_tone: str

        | 音高名(A4=440Hz)。
        | 半角上げは#もしくは♯ 
        | 半角下げはbもしくは♭で与えられます。

    velocity: int
        子音速度

    flags: str, default ""
        フラグ(省略可)

    offset: float, default 0
        入力ファイルの読み込み開始位置(ms)

    target_ms: float, default 0

        | 出力ファイルの長さ(ms)
        | UTAUでは通常50ms単位に丸めた値が渡される。

    fixed_ms: float, default 0
        offsetからみて通常伸縮しない長さ(ms)

    end_ms: float, default 0
        | 入力ファイルの読み込み終了位置(ms)(省略可 default:0)
        | 正の数の場合、ファイル末尾からの時間
        | 負の数の場合、offsetからの時間

    intensity: int, default 100
        音量。0～200(省略可)

    modulation: int, default 0
        モジュレーション。0～200(省略可)

    tempo: str, default "!120"

        | ピッチのテンポ
        | 数字の頭に!がついた文字列

    pitchbend: str, default ""

        | ピッチベンド。(省略可)
        | -2048～2047までの12bitの2進数をbase64で2文字の文字列に変換し、
        | 同じ数字が続く場合ランレングス圧縮したもの

    stp : float
        入力wavの先頭のオフセットをmsで指定する。

    output_ms: float
        wavtoolが出力する長さ

    
    envelope : list
        エンベロープのパターンは以下のいずれかです。
            >>> p1 p2
            >>> p1 p2 p3 v1 v2 v3 v4
            >>> p1 p2 p3 v1 v2 v3 v4 ove
            >>> p1 p2 p3 v1 v2 v3 v4 ove p4
            >>> p1 p2 p3 v1 v2 v3 v4 ove p4 p5 v5
        | p1,p2,p3,p4,p5,ove : float
        | v1,v2,v3,v4,v5 : int

    '''
    _input_path: str
    _output_path: str
    _target_tone: str
    _velocity: int
    _flags: str
    _offset: float
    _target_ms: int
    _fixed_ms: float
    _end_ms: float
    _intensity: int
    _modulation: int
    _tempo: str
    _pitchbend: str
    _stp: float
    _envelope: str
    _cache_path: str
    _output_ms: float
    _require_resamp: bool = True

    @property
    def input_path(self) -> str:
        return self._input_path
    
    @property
    def output_path(self) -> str:
        return self._output_path

    @property
    def target_tone(self) -> str:
        return self._target_tone
    
    @property
    def velocity(self) -> int:
        return self._velocity

    @property
    def flags(self) -> str:
        return self._flags
    
    @property
    def offset(self) -> float:
        return self._offset
    
    @property
    def target_ms(self) -> int:
        return self._target_ms
    
    @property
    def fixed_ms(self) -> float:
        return self._fixed_ms
    
    @property
    def end_ms(self) -> float:
        return self._end_ms
    
    @property
    def intensity(self) -> int:
        return self._intensity
    
    @property
    def modulation(self) -> int:
        return self._modulation

    @property
    def tempo(self) -> str:
        return self._tempo
    
    @property
    def pitchbend(self) -> str:
        return self._pitchbend
    
    @property
    def stp(self) -> float:
        return self._stp

    @property
    def envelope(self) -> str:
        return self._envelope
    
    @property
    def cache_path(self) -> str:
        return self._cache_path
    
    @property
    def output_ms(self) -> float:
        return self._output_ms

    @property
    def require_resamp(self) -> bool:
        return self._require_resamp

    def __init__(self, note: Note, vb: VoiceBank, cachedir: str, output: str, mode2: bool = True):
        '''
        Parameters
        ----------
        note: Note
            | 変換するノート。
            | noteとnote.nextは事前にapply_otoを実施しておくこと

        vb: VoiceBank
            音源

        cachedir: str
            resampが中間ファイルを出力するフォルダ

        output: str
            wavtoolがwavを出力するフォルダ

        mode2: bool True
            | ピッチデータの扱い。
            | Trueの場合、PBS,PBY,PBM,PBW,Vibratoを解釈
            | Falseの場合、Pitches,PBStartを解釈
        '''
        self._input_path = os.path.join(vb.dirpath, note.atFileName.value)
        self._output_path = output
        self._target_tone = note.notenum.get_tone_name()
        self._velocity = note.velocity.value
        self._flags = note.flags.value
        if note.next is None:
            self._output_ms = note.msLength + note.atPre.value
        else:
            self._output_ms = note.msLength + note.atPre.value + note.next.atOve.value - note.next.atPre.value
        self._target_ms = (round((self._output_ms + note.atStp.value) / 50) + 1 ) * 50
        if  vb.oto.haskey(note.atAlias.value):
            self._offset = vb.oto[note.atAlias.value].offset
            self._fixed_ms = vb.oto[note.atAlias.value].consonant
            self._end_ms = vb.oto[note.atAlias.value].blank
        else:
            self._offset = 0
            self._fixed_ms = 0
            self._end_ms = 0
            self._require_resamp = False
        self._intensity = note.intensity.value
        self._modulation = note.modulation.value
        self._tempo = "!{:.2f}".format(note.tempo.value)
        if note.lyric.value != "R":
            self._pitchbend = self._get_pitches(note, mode2)
        else:
            self._pitchbend = ""
        self._stp = note.atStp.value
        if note.envelope.hasValue:
            if "%" in note.envelope.value:
                self._envelope = note.envelope.value.replace("%", str(note.atOve)).replace(","," ")
            else:
                self._envelope = note.envelope.value.replace(","," ") + " " +str(note.atOve)
        else:
            self._envelope = settings.DEFAULT_ENV.replace("%", str(note.atOve))
        self._cache_path = os.path.join(cachedir, "{}_{}_{}_{}.wav".format(note.num.value[1:],
                                                note.atAlias.value.replace(" ","+"),
                                                note.notenum.get_tone_name(),
                                                self._get_cache_hash(note)))

    def _get_cache_hash(self, note: Note) -> str:
        '''
        resampが使用する各パラメータを使用して、ハッシュ値を生成します。

        Parameters
        ----------
        note: Note
            | 変換するノート。
            | noteとnote.nextは事前にapply_otoを実施しておくこと

        Returns
        -------
        hash: str
            6桁のハッシュ文字

        '''
        return hashlib.md5("{}_{}_{}_{}_{}_{}_{}_{}".format(note.pre.value,
                                                            note.stp.value,
                                                            note.velocity.value,
                                                            note.flags.value,
                                                            note.intensity.value,
                                                            note.modulation.value,
                                                            note.tempo.value,
                                                            self._pitchbend,
                                                            ).encode()).hexdigest()[:6]

    def _get_pitches(self, note: Note, mode2: bool) -> str:
        '''
        | mode2の値に応じてピッチ列を返します。
        | Falseの場合、Pitches,PBStartを解釈
        | Trueの場合、PBS,PBY,PBM,PBW,Vibrato,next.PBS,next.PBY.next.PBM,next.PBW,prev.PBS,prev.PBY,prev.PBM,prev.PBW,prev.Vibratoを解釈

        Parameters
        ----------
        note: Note
            | 変換するノート。
            | noteとnote.nextは事前にapply_otoを実施しておくこと

        mode2: bool True
            | ピッチデータの扱い。
            | Trueの場合、PBS,PBY,PBM,PBW,Vibratoを解釈
            | Falseの場合、Pitches,PBStartを解釈

        Returns
        -------
        pitchbend: str
            | -2048～2047までの12bitの2進数をbase64で2文字の文字列に変換し、
            | 同じ数字が続く場合ランレングス圧縮したもの

        '''
        t: np.ndarray = PyRwu.pitch.getPitchRange(self._tempo, self._target_ms, 44100)
        offset: float = note.atPre.value + note.atStp.value
        if mode2:
            base_pitches: np.ndarray = self._get_base_pitches(note, t)
            if note.prev is not None and note.prev.lyric.value != "R":
                base_pitches += self._interp_pitches(note.prev, t, offset - note.prev.msLength)
                base_pitches += self._get_vibrato_pitches(note.prev, t, offset - note.prev.msLength)
            base_pitches += self._interp_pitches(note, t, offset)
            base_pitches += self._get_vibrato_pitches(note, t, offset)
            if note.next is not None and note.next.lyric.value != "R":
                base_pitches += self._interp_pitches(note.next, t, offset + note.msLength)
        else:
            base_pitches: np.ndarray = np.zeros_like(t, dtype = np.int16)
            start_ms: float = offset + note.pbStart.value #pbstartは負の数
            start: int = np.where(t>= start_ms)[0][0]
            end: int = start + len(note.pitches.value)
            print(note.pbStart.value)
            print(offset)
            print(start)
            print(end)
            if start < end:
                base_pitches[start:end] = np.array(note.pitches.value)
        return self.encodeRunLength(self.encodeBase64(base_pitches))

    def _get_base_pitches(self, note: Note, t:np.ndarray) -> np.ndarray:
        '''
        noteとその前後のpbsとnotenumを使って、基準ピッチ列を返します。
        
        Parameters
        ----------
        note: Note
            | 変換するノート。
            | noteとnote.nextは事前にapply_otoを実施しておくこと

        t: np.ndarray
            ピッチ点の時間列

        Returns
        -------
        base_pitch: np.ndarray
            | 基準ピッチ列
            | prev.pbs.timeより前の点 = 0
            | prev.pbs.time→pbs.timeの点 = (prev.notenum - notenum) * 100
            | pbs.time → next.pbs.timeの点 = 0
            | next.pbs.timeより後ろの点 = (next.notenum - notenum) * 100
        '''
        base_pitches: np.ndarray = np.zeros_like(t, dtype = np.int16)
        offset: float = note.atPre.value + note.atStp.value
        start: int
        end: int
        if note.prev is not None and note.prev.lyric.value != "R":
            prev_offset: float = offset - note.prev.msLength
            if note.prev.pbs.time + prev_offset < 0:
                start = 0
            else:
                start = np.where(t >= note.prev.pbs.time + prev_offset)[0][0]
            if t[0]<=note.pbs.time + offset:
                end = np.where(t < note.pbs.time + offset)[0][-1]
            else:
                end = 0
            if start < end:
                base_pitches[start:end] = (note.prev.notenum.value - note.notenum.value) * 100
        if note.next is not None and note.next.lyric.value != "R":
            next_offset: float = offset + note.msLength
            if t[-1] >= note.next.pbs.time + next_offset:
                start = np.where(t >= note.next.pbs.time + next_offset)[0][0]
                base_pitches[start:] = (note.next.notenum.value - note.notenum.value) * 100
        return base_pitches

    def _interp_pitches(self, note: Note, t:np.ndarray, offset:float) -> np.ndarray:
        '''
        noteのpbs,pby,pbw,pbmとnote.prev.notenumを使ってピッチ列を返します。
        
        Parameters
        ----------
        note: Note
            | 変換するノート。
            | noteとnote.nextは事前にapply_otoを実施しておくこと

        t: np.ndarray
            ピッチ点の時間列

        offset: float
            pbs.timeなどの時間のずれ

        Returns
        -------
        pitches: np.ndarray
            ピッチ列
        '''
        pitches: np.ndarray = np.zeros_like(t, dtype = np.int16)

        if not note.pbs.hasValue:
            return pitches

        x, y, mode = self._get_interp_base(note, offset)
            
        start: int
        end: int
        for i in range(len(x)):
            if i==0:
                continue
            if t[-1] <= x[i]:
                continue
            start, end, cycle, height, phase = self._get_interp_param(x, y, t, i)
            if start >= end:
                continue
            if(mode[i-1] == ""):
                #cos(-pi) → cos(0)の補完
                pitches[start:end+1] = self._interp_default(cycle, height, phase, y[i-1])
            elif (mode[i-1] == "s"):
                #線形補完
                pitches[start:end+1] = self._interp_s(cycle, height, phase, y[i-1])
            elif (mode[i-1] == "r"):
                #sin(0) → sin(pi/2)の補完
                pitches[start:end+1] = self._interp_r(cycle, height, phase, y[i-1])
            elif (mode[i-1] == "j"):
                #cos(0) → cos(pi/2)の補完
                pitches[start:end+1] = self._interp_j(cycle, height, phase, y[i-1])

        return pitches

    @staticmethod
    def _interp_default(cycle, height, phase, offset):
        return ((np.cos(np.pi / cycle * phase - np.pi) + 1) * height / 2 + offset)
    
    @staticmethod
    def _interp_s(cycle, height, phase, offset):
        return height / cycle * phase + offset
    
    @staticmethod
    def _interp_r(cycle, height, phase, offset):
        return np.sin(np.pi / cycle / 2 * phase) * height + offset
    
    @staticmethod
    def _interp_j(cycle, height, phase, offset):
        return (-np.cos(np.pi / cycle / 2 * phase)+1) * height + offset

    def _get_interp_param(self, x: np.ndarray, y: np.ndarray, t: np.ndarray, i: int) -> Tuple[int, int, float, float, np.ndarray]:
        '''
        x[i-1]～x[i]の間のピッチパラメータを求めるための諸元を求めます。
        
        Parameters
        ----------
        x: np.ndarray
            ポルタメントの時間間隔

        y: np.ndarray
            ポルタメントの音高

        t: np.ndarray
            ピッチ点の時間列

        i: xのindex

        Returns
        -------
        start: int
            ピッチを補完する範囲の始点

        end: int
            ピッチを補完する範囲の終点

        cycle: float
            補完範囲の時間

        height: float
            補完範囲の音高差

        phase: np.ndarray
            t[start:end+1]をx[i-1]からの経過時間に変換したもの
        '''
        start: int = np.where(t>=x[i-1])[0][0]
        if t[0]<x[i]:
            end: int = np.where(t<x[i])[0][-1]
        else:
            end: int = 0
        cycle: float = x[i] - x[i-1]
        height: int = y[i] - y[i-1]
        phase: np.ndarray = t[start:end+1] - x[i-1]
        return start, end, cycle, height, phase

    def _get_interp_base(self, note: Note, offset:float) -> Tuple[np.ndarray, np.ndarray, list]:
        '''
        noteのpbs,pby,pbw,pbmとnote.prev.notenumを使ってinterpに使用するx,y,modeを求める
        
        Parameters
        ----------
        note: Note
            | 変換するノート。
            | noteとnote.nextは事前にapply_otoを実施しておくこと

        offset: float
            pbs.timeなどの時間のずれ

        Returns
        -------
        x: np.ndarray
            ポルタメントの時間間隔

        y: np.ndarray
            ポルタメントの音高

        mode: list
            ピッチの補完方法
        '''
        x:np.ndarray = np.zeros(len(note.pbw.value) + 1)
        for i in range(len(note.pbw.value)):
            x[i+1] = x[i] + note.pbw.value[i]
        x = x + note.pbs.time + offset
        y: np.ndarray = np.zeros_like(x)
        if note.prev is not None and note.prev.lyric.value != "R":
            y[0] = (note.prev.notenum.value - note.notenum.value) * 100
        else:
            y[0] = note.pbs.height * 10
        for i in range(len(note.pby.value)):
            y[i+1] = note.pby.value[i] * 10
        mode: list = (note.pbm.value + [""]*(len(x)-1))[:len(x)-1]

        return x, y, mode
    
    def _get_vibrato_pitches(self, note:Note, t:np.ndarray, offset:float) -> np.ndarray:
        '''
        noteのpbs,pby,pbw,pbmとnote.prev.notenumを使ってピッチ列を返します。
        
        Parameters
        ----------
        note: Note
            | 変換するノート。
            | noteとnote.nextは事前にapply_otoを実施しておくこと

        t: np.ndarray
            ピッチ点の時間列

        offset: float
            時間のずれ

        Returns
        -------
        pitches: np.ndarray
            ピッチ列
        '''
        pitches: np.ndarray = np.zeros_like(t, dtype = np.int16)
        if not note.vibrato.hasValue:
            return pitches
        start_ms: float = offset + note.msLength * (100 - note.vibrato.length) / 100
        end_ms: float = offset + note.msLength
        start: int = np.where(t>=start_ms)[0][0]
        if t[0] < end_ms:
            end: int = np.where(t<end_ms)[0][-1]
        else:
            end: int =0
        if start >= end:
            return pitches
                
        phase: np.ndarray = t[start:end + 1] - start_ms
        phase_offset: float = 2 * np.pi * note.vibrato.phase /100

        fade = self._get_vibrato_fade(note, phase)

        height: np.ndarray = fade * int(note.vibrato.depth)
        pitches[start:end+1] = np.round((np.sin(2 * np.pi / note.vibrato.cycle * phase + phase_offset) + note.vibrato.height/100) * height)
        return pitches

    def _get_vibrato_fade(self, note:Note, t:np.ndarray) -> np.ndarray:
        vibrato_ms: float = note.msLength * note.vibrato.length / 100
        fadeintime: float = vibrato_ms * note.vibrato.fadeInTime / 100
        fadeout_start_ms: float = vibrato_ms - vibrato_ms * note.vibrato.fadeOutTime / 100
        fade:np.ndarray = np.ones_like(t,dtype=np.float64)
        for i in range(len(t)):
            if t[i] <= fadeintime and fadeintime != 0:
                fade[i] =  t[i] / fadeintime
            elif t[i] >= fadeout_start_ms:
                fade[i] =  1 - ((t[i] - fadeout_start_ms) / (vibrato_ms - fadeout_start_ms))
        return fade

    @staticmethod
    def encodeBase64Core(value: int) -> str:
        '''
        0～63の数値を受け取り、1文字のstrを返す。

        Parameters
        ----------
        value: int

        Returns
        -------
        result: str
        '''
        if value < 26: #A-Z
            return chr(value + ord("A"))
        elif value < 52:
            return chr(value + ord("a") - 26)
        elif value < 62:
            return chr(value + ord("0") - 52)
        elif value == 62:
            return "+"
        else:
            return "/"

    @staticmethod
    def encodeBase64(values: np.ndarray) -> list:
        '''
        -2048 ～ 2047の数字を受け取り、文字列を返します。

        Parameters
        ----------
        values: np.ndarray
            -2048 ～ 2047のint列

        Returns
        -------
        result: list
            base64にエンコードした2桁の文字列のリスト
        '''
        result: list = []
        for value in values:
            tmp = value
            if value < 0:
                tmp += 4096
            result.append(RenderNote.encodeBase64Core(int(tmp/64)) + RenderNote.encodeBase64Core(tmp&63))
        return result

    @staticmethod
    def encodeRunLength(values: list) -> str:
        '''
        | base64エンコードした文字列のリストを受け取り、ランレングス圧縮します。
        | 2文字一組とし、#num#はひとつ前の組の繰り返し回数を表します。
    
        >>> [AA, AB, AC] → AAABAC
        >>> [AA, AA, AA, AA] → AA#3#


        Parameters
        ----------
        values: list

        Returns
        -------
        result: str
        '''
        result: str = ""
        tmp: str = ""
        num: int = 0
        for value in values:
            if tmp != value:
                tmp = value
                if num != 0:
                    result += "#{}#".format(num)
                num = 0
                result += value
            else:
                num += 1
        return result