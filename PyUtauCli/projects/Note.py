
from .Entry import *
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

    hasTempo: bool, default False
        tempoの値が、このノートに設定されたものか、前のノートやプロジェクトのデフォルトから継承されたものかを管理する。

    pre: PreEntry
        ノートの先行発声

    hasPre: bool, default False
        preの値が、このノートに設定されたものか、原音設定値を読み込んだものかを管理する。

    atPre: AtPreEntry
        | UTAUのパラメータ自動調整適用後の先行発声値
        | 前の音が休符以外の場合
        | AtPre = pre / (pre -ove) * prev.msLength/2
        | 前の音が休符の場合
        | AtPre = pre / (pre -ove) * prev.msLength

    ove: OveEntry
        ノートのオーバーラップ値。

    hasOve: bool, default False
        oveの値が、このノートに設定されたものか、原音設定値を読み込んだものかを管理する。

    atOve: AtOveEntry
        | UTAUのパラメータ自動調整適用後のオーバーラップ値
        | 前の音が休符以外の場合
        | AtOve = ove / (pre -ove) * prev.msLength/2
        | 前の音が休符の場合
        | AtOve = ove / (pre -ove) * prev.msLength

    stp: StpEntry
        ノートのstp値

    atStp: AtStpEntry
        | UTAUのパラメータ自動調整適用後のオーバーラップ値
        | atStp = Pre - atPre + stp で与えられる。

    atFileName: AtFileNameEntry
        このノートが参照しているファイルの音源ルートからの相対パス

    atAlias: AtAliasEntry
        このノートが参照している原音設定のエントリ

    velocity: VelocityEntry
        | このノートの子音速度。
        | 音源を再生するとき、固定範囲、先行発声、オーバーラップに以下の係数がかかる。
        | rate = 2 ** ((100-velocity)/100)

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
        | time;height
        | time,height
        | time
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
        | p1,p2,p3,v1,v2,v3,v4
        | p1,p2,p3,v1,v2,v3,v4,%,p4
        | p1,p2,p3,v1,v2,v3,v4,%,p4,p5,v5
        |
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

    hasFlags: bool
        flags値がこのノートに設定されたものか、プロジェクトのデフォルトによるものかを管理する。

    prev: Note, default None
        1つ前のノートへのポインタ

    next: note, default None
        1つ後ろのノートへのポインタ
    '''
    prev = None
    next = None
