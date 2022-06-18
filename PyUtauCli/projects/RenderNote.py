import os.path
import hashlib
import math

from typing import Tuple

import numpy as np
import PyRwu.pitch

from .Note import Note
from voicebank import VoiceBank

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
        self._offset = vb.oto[note.atAlias.value].offset
        if note.next is None:
            self._output_ms = note.msLength + note.atPre.value + note.atStp.value
        else:
            self._output_ms = note.msLength + note.atPre.value + note.atStp.value + note.next.atOve.value - note.next.atPre.value
        self._target_ms = (round((self._output_ms) / 50) + 1 ) * 50
        self._fixed_ms = vb.oto[note.atAlias.value].consonant
        self._end_ms = vb.oto[note.atAlias.value].blank
        self._intensity = note.intensity.value
        self._modulation = note.modulation.value
        self._tempo = "!{:.2f}".format(note.tempo.value)
        self._pitchbend = self._get_pitches(note, mode2)
        self._stp = note.atStp.value
        #TODO envelopeが空欄の場合の処理が必要
        self._envelope = note.envelope.value.replace("%", str(note.ove)).replace(","," ")
        #self._cache_path = os.path.join(cachedir, "{}_{}_{}_{}".format(int(note.num.value[1:],
        #                                                                   note.atAlias.value.replace(" ","+"),
        #                                                                   note.notenum.get_tone_name(),
        #                                                                   self._get_cache_hash(note))))
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
        #todo
        pass
        #hashlib.md5("{}_{}_{}_{}".format(note.pre.value,
        #                                 note.stp.value,
        #                                 note.velocity.value,
        #                                 note.flags.value,
        #                                 ).encode()).hexdigest()[:6]

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
        base_pitches: np.ndarray = self._get_base_pitches(note, t)
        if note.prev is not None and note.prev.lyric.value != "R":
            base_pitches += self._interp_pitches(note.prev, t, offset - note.prev.msLength)
        base_pitches += self._interp_pitches(note, t, offset)
        if note.next is not None and note.next.lyric.value != "R":
            base_pitches += self._interp_pitches(note.next, t, offset + note.msLength)

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
        base_pitches: np.ndarray = np.zeros_like(t)
        offset: float = note.atPre.value + note.atStp.value
        start: int
        end: int
        if note.prev is not None and note.prev.lyric.value != "R":
            prev_offset: float = offset - note.prev.msLength
            if note.prev.pbs.time + prev_offset < 0:
                start = 0
            else:
                start = np.where(t >= note.prev.pbs.time + prev_offset)[0][0]
            end = np.where(t < note.pbs.time + offset)[0][-1]
            base_pitches[start:end] = (note.prev.notenum.value - note.notenum.value) * 100
        if note.next is not None and note.next.lyric.value != "R":
            next_offset: float = offset + note.msLength
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
        pitches: np.ndarray = np.zeros_like(t)

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
            elif (mode.value[i-1] == "s"):
                #線形補完
                pitches[start:end+1] = self._interp_s(cycle, height, phase, y[i-1])
            elif (mode.value[i-1] == "r"):
                #sin(0) → sin(pi/2)の補完
                pitches[start:end+1] = self._interp_r(cycle, height, phase, y[i-1])
            elif (mode.value[i-1] == "j"):
                #cos(0) → cos(pi/2)の補完
                pitches[start:end+1] = self._interp_j(cycle, height, phase, y[i-1])
        return pitches

    def _interp_default(self, cycle, height, phase, offset):
        return (math.cos(math.pi / cycle * phase - math.pi) + 1) * height / 2 + offset

    def _interp_s(self, cycle, height, phase, offset):
        return height / cycle * phase + offset

    def _interp_r(self, cycle, height, phase, offset):
        return math.sin(math.pi / cycle / 2 * phase) * height + offset

    def _interp_j(self, cycle, height, phase, offset):
        return (math.cos(math.pi / cycle / 2 * phase)+1) * height + offset

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
        start: int = np.where(t>x[i])[0][0]
        end: int = np.where(t<x[i])[0][-1]
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
        x = x - note.pbs.time + offset
        y: np.ndarray = np.zeros_like(x)
        if note.prev is not None and note.prev.lyric.value != "R":
            y[0] = (note.prev.notenum.value - note.notenum.value) * 100
        else:
            y[0] = note.pbs.height * 10
        for i in range(len(note.pby.value)):
            y[i+1] = y[i] * 10
        mode: list = (note.pbm.value + [""]*len(x-1))[:len(x-1)]

        return x, y, mode