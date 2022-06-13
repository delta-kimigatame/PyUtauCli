import os. path

from .Entry import *
from voicebank.prefixmap import PrefixMap
from voicebank.oto import Oto


class Note:
    '''
    ustやプラグインでのNoteを扱います。

    Attributes
    ----------
    num: NumberEntry
        ノート番号。#0000や#INSERT,#DELETEなどの形で与えられます。

    length: LengthEntry
        ノートのtick数。4分音符=480

    lyric: LyricEntry
        ノートの歌詞

    notenum: NoteNumEntry
        ノートの音高。C4=60

    tempo: TempoEntry
        ノートのbpm。


    pre: PreEntry
        ノートの先行発声


    atPre: AtPreEntry
        | UTAUのパラメータ自動調整適用後の先行発声値
        | 前の音が休符以外の場合

            >>> AtPre = pre / (pre -ove) * prev.msLength/2

        | 前の音が休符の場合

            >>> AtPre = pre / (pre -ove) * prev.msLength

    ove: OveEntry
        ノートのオーバーラップ値。


    atOve: AtOveEntry
        | UTAUのパラメータ自動調整適用後のオーバーラップ値
        | 前の音が休符以外の場合

            >>> AtOve = ove / (pre -ove) * prev.msLength/2

        | 前の音が休符の場合

            >>> AtOve = ove / (pre -ove) * prev.msLength

    stp: StpEntry
        ノートのstp値

    atStp: AtStpEntry
        | UTAUのパラメータ自動調整適用後のオーバーラップ値

            >>> atStp = Pre - atPre + stp

    atFileName: AtFileNameEntry
        このノートが参照しているファイルの音源ルートからの相対パス

    atAlias: AtAliasEntry
        このノートが参照している原音設定のエントリ

    velocity: VelocityEntry
        | このノートの子音速度。
        | 音源を再生するとき、固定範囲、先行発声、オーバーラップに以下の係数がかかる。

            >>> rate = 2 ** ((100-velocity)/100)

    intensity: IntensityEntry
        | このノートの音量。
        | resamplerのターゲット音量が、100で-6dB、200で0dB、0で-infとなる。

    modulation: ModulationEntry
        | このノートのモジュレーション
        | 0の時は音高通りの音程で、100の時は原音の音高のぶれを再現する。

    pitches: PitchesEntry
        mode1で扱うピッチ数列。

    pbStart: PBStartEntry
        ノートの頭から見てmode1のピッチのが何msから始まるか

    pbs: PBSEntry
        | mode2のピッチの開始点。以下のいずれかの書式で与えられる。

            >>> time;height
            >>> time,height
            >>> time

        | timeの単位はms、heightの単位はcent

    pby: PBYEntry
        mode2のピッチ制御点の音高列。制御点の数-2個(最初と最後を除く)与えられる。単位はcent

    pbw: PBWEntry
        mode2のピッチの制御点どおしの間隔を表す時間列。制御点の数-1個与えられる。単位はms

    pbm: PBMEntry
        | mode2のピッチの制御点どおしをどのように補完するかを表す値列。制御点の数-1個与えられる。
        | ""の場合、cos(-pi) → cos(0)の補完
        | "s"の場合、線形保管
        | "r"の場合、sin(0) → sin(pi/2)の補完
        | "j"の場合、cos(0) → cos(pi/2)の補完

    envelope: EnvelopeEntry
        | このノートの音量の変化。以下のいずれかの書式で与えられる。pはfloat(ms)、vはint

            >>> p1,p2,p3,v1,v2,v3,v4
            >>> p1,p2,p3,v1,v2,v3,v4,%,p4
            >>> p1,p2,p3,v1,v2,v3,v4,%,p4,p5,v5

        | p1はノート頭からのms
        | p2はp1からのms
        | p3はp4から前向きのms
        | p4はノート末尾から前向きのms
        | p5はp2からのms

    vibrato: VibratoEntry
        | このノートのビブラート。
        | lengthはノート長に対するビブラートがかかる範囲の割合
        | cycleはビブラートにおけるsin派1周にかかる時間(ms)
        | depthはビブラートのsin派の高さ(cent)
        | fadeInTimeはビブラートの波の大きさが最大になるまでの時間をビブラート全体の長さに対する割合で指定
        | fadeOutTimeはビブラートの波の大きさが0になるまでの時間をビブラート全体の長さに対する割合で指定
        | phaseは位相がsin派一周の何%ずれているか
        | heightは、0のとき波の中心が、-100のとき波の頂点が0に、100のとき波の底が0となるような割合

    label: LabelEntry
        このノートにつけられたラベル

    direct: DirectEntry
        Trueのとき、resamplerを経由せず直接wavtoolに値が送られる。

    region: RegionEntry
        「選択範囲に名前を付ける」でつけた名前の開始位置

    region_end: RegionEndEntry
        「選択範囲に名前を付ける」でつけた名前の終了位置

    flags: FlagsEntry
        このノートに適用されるのフラグ

    prev: Note, default None
        1つ前のノートへのポインタ

    next: note, default None
        1つ後ろのノートへのポインタ
    '''
    num: NumberEntry
    length: LengthEntry
    lyric: LyricEntry
    notenum: NoteNumEntry
    tempo: TempoEntry
    pre: PreEntry
    atPre: AtPreEntry
    ove: OveEntry
    atOve: AtOveEntry
    stp: StpEntry
    atStp: AtStpEntry
    atFileName: AtFileNameEntry
    atAlias: AtAliasEntry
    velocity: VelocityEntry
    intensity: IntensityEntry
    modulation: ModulationEntry
    pitches: PitchesEntry
    pbStart: PBStartEntry
    pbs: PBSEntry
    pby: PBYEntry
    pbm: PBMEntry
    pbw: PBWEntry
    envelope: EnvelopeEntry
    vibrato: VibratoEntry
    label: LabelEntry
    direct: DirectEntry
    region: RegionEntry
    region_end: RegionEndEntry
    flags: FlagsEntry
    prev = None
    next = None

    def __init__(self):
        self.num = NumberEntry()
        self.length = LengthEntry()
        self.lyric = LyricEntry()
        self.notenum = NoteNumEntry()
        self.tempo = TempoEntry()
        self.pre = PreEntry()
        self.atPre = AtPreEntry()
        self.ove = OveEntry()
        self.atOve = AtOveEntry()
        self.stp = StpEntry()
        self.atStp = AtStpEntry()
        self.atFileName = AtFileNameEntry()
        self.atAlias = AtAliasEntry()
        self.velocity = VelocityEntry()
        self.intensity = IntensityEntry()
        self.modulation = ModulationEntry()
        self.pitches = PitchesEntry()
        self.pbStart = PBStartEntry()
        self.pbs = PBSEntry()
        self.pby = PBYEntry()
        self.pbm = PBMEntry()
        self.pbw = PBWEntry()
        self.envelope = EnvelopeEntry()
        self.vibrato = VibratoEntry()
        self.label = LabelEntry()
        self.direct = DirectEntry()
        self.region = RegionEntry()
        self.region_end = RegionEndEntry()
        self.flags = FlagsEntry()
        self.prev = None
        self.next = None

    def apply_oto(self, oto: Oto, prefix: PrefixMap):
        '''
        | 原音設定値を読み込んで、pre,oveを更新します。
        | もし、パラメータが初期化されていない場合、atPre,atOve,atStp,atAlias,atFileNameも更新します。

        Parameters
        ----------
        oto: Oto
            原音設定ファイル

        prefix: prefixMap
            エイリアスの推定に使用します。

        Raises
        ------
        ValueError
            lyricもしくはnotenumが初期化されていない場合
        '''
        alias: str
        if not self.lyric.hasValue:
            raise ValueError("lyric is not initial")
        if not self.notenum.hasValue:
            raise ValueError("notenum is not initial")

        alias = self._init_alias(oto, prefix)
        self._apply_oto_to_pre(alias, oto)
        self._apply_oto_to_ove(alias, oto)
        self.autofit_atparam()

    def _init_alias(self, oto: Oto, prefix: PrefixMap) -> str:
        '''
        | 歌詞、音高、prefix.mapを参照してエイリアスを特定します。
        | 一致する原音設定レコードが見つからない場合、""を返します。
        | atAliasが値を持っていなかった場合、atAlias,atFileNameを更新します。

        Parameters
        ----------
        oto: Oto
            原音設定ファイル

        prefix: prefixMap
            エイリアスの推定に使用します。

        Returns
        -------
        alias: str, default ""
        '''
        if self.atAlias.hasValue:
            return self.atAlias.value
        elif oto.haskey(prefix[self.notenum.value].prefix + self.lyric.value + prefix[self.notenum.value].suffix):
            self.atAlias.value = prefix[self.notenum.value].prefix + self.lyric.value + prefix[self.notenum.value].suffix
            self.atFileName.value = os.path.join(oto[self.atAlias.value].otopath, oto[self.atAlias.value].filename)
            return prefix[self.notenum.value].prefix + self.lyric.value + prefix[self.notenum.value].suffix
        elif oto.haskey(self.lyric.value):
            self.atAlias.value = self.lyric.value
            self.atFileName.value = os.path.join(oto[self.lyric.value].otopath, oto[self.lyric.value].filename)
            return self.lyric.value
        else:
            return ""

    def _apply_oto_to_pre(self, alias: str, oto: Oto):
        '''
        | 原音設定値を読み込んで、preを更新します。
        | もしalias=""の場合、0で更新します。

        Parameters
        ----------
        alias: str
            otoのkeyになるエイリアス
        oto: Oto
            原音設定ファイル
        '''
        if self.pre.hasValue:
            return
        if alias == "":
            self.pre.value = 0
        else:
            self.pre.value = oto[alias].pre
        self.pre.hasValue = False

    def _apply_oto_to_ove(self, alias: str, oto: Oto):
        '''
        | 原音設定値を読み込んで、oveを更新します。
        | もしalias=""の場合、0で更新します。

        Parameters
        ----------
        alias: str
            otoのkeyになるエイリアス
        oto: Oto
            原音設定ファイル
        '''
        if self.ove.hasValue:
            return
        if alias == "":
            self.ove.value = 0
        else:
            self.ove.value = oto[alias].ove
        self.ove.hasValue = False

    def autofit_atparam(self):
        '''
        pre,ove,stp,velocity,prev.length,prev.tempoを勘案して、atpre,atove,atstpを更新します。

        Raises
        ------
        ValueError
            prev.lengthがNone出ないにもかかわらず、lyric,length,tempoの値が与えられていないとき。
        '''
        if self.prev is None:
            # 前のノートが存在しない場合、自動調整は不要。
            self.atPre.value = self.pre.value
            self.atOve.value = self.ove.value
            self.atStp.value = self.stp.value
            return

        if not self.prev.lyric.hasValue:
            raise ValueError("prev lyric is not initial")

        prevMsLength: int = self.prev.msLength
        realPre: float = self.pre.value * self.velocity.rate
        realOve: float = self.ove.value * self.velocity.rate
        realStp: float = self.stp.value * self.velocity.rate
        if self.prev.lyric.value != "R":
            prevMsLength /= 2

        if prevMsLength < (realPre - realOve):
            self.atPre.value = realPre / (realPre - realOve) * prevMsLength
            self.atOve.value = realOve / (realPre - realOve) * prevMsLength
            self.atStp.value = realPre - self.atPre.value + realStp
        else:
            self.atPre.value = realPre
            self.atOve.value = realOve
            self.atStp.value = realStp

    @property
    def msLength(self) -> int:
        '''
        tempoとlengthからmsを計算して返します。

        Returns
        -------
        msLength: int

        Raises
        ------
        ValueError
            tempoもしくはlengthが初期化されていないとき。
        '''
        if not self.length.hasValue:
            raise ValueError("length is not initial")

        if not self.tempo.hasValue:
            raise ValueError("tempo is not initial")

        return int(60 / self.tempo.value * self.length.value / 480 * 1000)
