from voicebank.oto import Oto
from voicebank.prefixmap import PrefixMap
from .Note import Note
import settings.logger
import settings.settings
import os
import os.path
import sys
import re
import traceback
from logging import Logger
sys.path.append('../')


default_logger = settings.logger.get_logger(__name__, False)


class Ust:
    '''
    UTAU sequence textファイルを扱います。

    Attributes
    ----------
    filepath: str
        ustのファイルパス

    version: float, default 1.2
        ustのバージョン。

    project_name: str
        プロジェクト名

    voice_dir: str
        | 音源フォルダへのパス。
        | %voice%はsettings.settings.VOICE_ROOTのこと。

    cache_dir: str
        | wavキャッシュの保存先

    output_file: string
        書き出すwavファイルのパス

    tempo: float
        プロジェクトのbpm

    wavtool: str
        wavtoolのパス

    resamp: str
        resamplerのパス

    flags: str
        デフォルトのフラグ

    mode2: bool, default False
        ピッチのmode2が有効かどうか

    utf8: bool, default False
        ustがutf8で保存されているかどうか

    notes: List of Note
        Noteの配列
    '''

    filepath: str
    _version: float = 1.2
    project_name: str
    voice_dir: str
    cache_dir: str
    output_file: str
    tempo: float
    wavtool: str
    resamp: str
    flags: str
    mode2: bool = False
    utf8: bool = False
    notes: list = []

    @property
    def version(self) -> float:
        return self._version

    def __init__(self, filepath: str, *, logger: Logger = None):
        self.logger = logger or default_logger
        self.filepath = filepath

    def load(self, filepath: str = ""):
        '''
        self.filepathもしくはfilepathのファイルを読み込みます。

        Parameters
        ----------
        filepath: str, default ""
            読み込むファイルのパス。値が与えられた場合、self.filepathを更新します。

        Raises
        ------
        FileNotFoundError
            self.filepathのファイルが見つからなかった場合
        '''
        if filepath != "":
            self.filepath = filepath

        if not os.path.isfile(self.filepath):
            self.logger.error("{} is not found".format(self.filepath))
            raise FileNotFoundError("{} is not found".format(self.filepath))
        self.logger.info("{} is found. loading file.".format(self.filepath))
        seek: int = self._load_header()
        self.logger.info("loading header complete.")
        self._load_note(seek)
        self.logger.info("loading note complete.notes:{}".format(len(self.notes)))
        for i in range(len(self.notes)):
            if i != 0:
                self.notes[i].prev = self.notes[i - 1]
                self.notes[i - 1].next = self.notes[i]

    def _load_header(self) -> int:
        '''
        | self.filepathのファイルをシステムの文字コードもしくはcp932で1行ずつ読み込み、各パラメータを更新します。
        | self.filepathが存在することは事前に確認できているものとします。

        Returns
        -------
        cursor: int
            ヘッダ末尾の位置

        Raises
        ------
        UnicodeDecodeError
            ファイルがシステム既定でもcp932でも開けなかった場合
        '''
        notHeaderReg: re.Pattern = re.compile("\[#([0-9]+|PREV|NEXT)\]")
        cursor: int = 0
        try:
            with open(self.filepath, "r") as fr:
                cursor = self._load_head_helper(fr, notHeaderReg)
        except:
            try:
                with open(self.filepath, "r", encoding="cp932") as fr:
                    cursor = self._load_head_helper(fr, notHeaderReg)
            except UnicodeDecodeError as e:
                self.logger.error("can't read {}'s header. because required character encoding is system default or cp932".format(otopath))
                e.reason = "can't read {}'s header. because required character encoding is system default or cp932".format(otopath)
                raise e
        return cursor

    def _load_head_helper(self, fr, notHeaderReg: re.Pattern) -> int:
        '''
        Returns
        -------
        cursor: int
            ヘッダ末尾の位置
        '''

        cursor: int = 0
        line: str = fr.readline().replace("\n", "")
        while not notHeaderReg.fullmatch(line):
            if line == "[#VERSION]":
                self.version = float(fr.readline().replace("\n", "").replace("UST Version", ""))
            elif line.startswith("Tempo="):
                self.tempo = line.replace("Tempo=", "")
            elif line.startswith("Project="):
                self.project_name = line.replace("Project=", "")
            elif line.startswith("VoiceDir="):
                self.voice_dir = line.replace("VoiceDir=", "")
            elif line.startswith("OutFile="):
                self.output_file = line.replace("OutFile=", "")
            elif line.startswith("CacheDir="):
                self.cache_dir = line.replace("CacheDir=", "")
            elif line.startswith("Tool1="):
                self.wavtool = line.replace("Tool1=", "")
            elif line.startswith("Tool2="):
                self.resamp = line.replace("Tool2=", "")
            elif line.startswith("Flags="):
                self.flags = line.replace("Flags=", "")
            elif line.startswith("Mode2="):
                self.mode2 = bool(line.replace("Mode2=", ""))
            cursor = fr.tell()
            line = fr.readline().replace("\n", "")
        return cursor

    def _load_note(self, seek: int):
        '''
        | self.filepathのファイルをcp932もしくはutf-8読み込み、各ノートのパラメータを更新します。
        | self.filepathが存在することは事前に確認できているものとします。

        Parameters
        ----------
        seek: int
            ヘッダの末尾

        Raises
        ------
        UnicodeDecodeError
            ファイルがcp932でもutf-8でも開けなかった場合
        '''
        lines: list = []
        tempo: float = self.tempo
        note: Note = None
        try:
            with open(self.filepath, "r", encoding="cp932") as fr:
                fr.seek(seek)
                lines = fr.read().replace("\r", "").split("\n")
        except:
            try:
                with open(self.filepath, "r", encoding="utf-8") as fr:
                    fr.seek(seek)
                    lines = fr.read().replace("\r", "").split("\n")
            except UnicodeDecodeError as e:
                self.logger.error("can't read {}'s body. because required character encoding is cp932 or utf-8".format(otopath))
                e.reason = "can't read {}'s body. because required character encoding is cp932 or utf-8".format(otopath)
                raise e

        for line in lines:
            if line.startswith("[#"):
                self.notes.append(Note())
                note = self.notes[-1]
                note.num.init(line.replace("[", "").replace("]", ""))
                note.tempo.init(tempo)
                note.tempo.hasValue = False
                note.flags.init(self.flags)
                note.flags.hasValue = False
            elif line.startswith("Length"):
                try:
                    note.length.init(line.replace("Length=", ""))
                except Exception as e:
                    note.length.init(480)
                    self.logger.warn("{} length can't init. because {}".format(note.num.value,
                                                                               traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("Lyric"):
                try:
                    note.lyric.init(line.replace("Lyric=", ""))
                except Exception as e:
                    note.lyric.init("あ")
                    self.logger.warn("{} lyric can't init. because {}".format(note.num.value,
                                                                              traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("NoteNum"):
                try:
                    note.notenum.init(line.replace("NoteNum=", ""))
                except Exception as e:
                    note.notenum.init(60)
                    self.logger.warn("{} notenum can't init. because {}".format(note.num.value,
                                                                                traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("Tempo"):
                try:
                    note.tempo.init(line.replace("Tempo=", ""))
                except Exception as e:
                    self.logger.warn("{} tempo can't init. because {}".format(note.num.value,
                                                                              traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("PreUtterance"):
                try:
                    note.pre.init(line.replace("PreUtterance=", ""))
                except Exception as e:
                    self.logger.warn("{} pre can't init. because {}".format(note.num.value,
                                                                            traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("@preuttr"):
                try:
                    note.atPre.init(line.replace("@preuttr=", ""))
                except Exception as e:
                    self.logger.warn("{} @preuttr can't init. because {}".format(note.num.value,
                                                                                 traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("VoiceOverlap"):
                try:
                    note.ove.init(line.replace("VoiceOverlap=", ""))
                except Exception as e:
                    self.logger.warn("{} ove can't init. because {}".format(note.num.value,
                                                                            traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("@overlap"):
                try:
                    note.atOve.init(line.replace("@overlap=", ""))
                except Exception as e:
                    self.logger.warn("{} @overlap can't init. because {}".format(note.num.value,
                                                                                 traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("StartPoint"):
                try:
                    note.stp.init(line.replace("StartPoint=", ""))
                except Exception as e:
                    self.logger.warn("{} stp can't init. because {}".format(note.num.value,
                                                                            traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("@stpoint"):
                try:
                    note.atStp.init(line.replace("@stpoint=", ""))
                except Exception as e:
                    self.logger.warn("{} @stpoint can't init. because {}".format(note.num.value,
                                                                                 traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("@filename"):
                try:
                    note.atFileName.init(line.replace("@filename=", ""))
                except Exception as e:
                    self.logger.warn("{} @filename can't init. because {}".format(note.num.value,
                                                                                  traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("@alias"):
                try:
                    note.atAlias.init(line.replace("@alias=", ""))
                except Exception as e:
                    self.logger.warn("{} @alias can't init. because {}".format(note.num.value,
                                                                               traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("Velocity"):
                try:
                    note.velocity.init(line.replace("Velocity=", ""))
                except Exception as e:
                    self.logger.warn("{} Velocity can't init. because {}".format(note.num.value,
                                                                                 traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("Intensity"):
                try:
                    note.intensity.init(line.replace("Intensity=", ""))
                except Exception as e:
                    self.logger.warn("{} Intensity can't init. because {}".format(note.num.value,
                                                                                  traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("Modulation"):
                try:
                    note.modulation.init(line.replace("Modulation=", ""))
                except Exception as e:
                    self.logger.warn("{} Modulation can't init. because {}".format(note.num.value,
                                                                                   traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("Pitches"):
                try:
                    note.pitches.init(line.replace("Pitches=", ""))
                except Exception as e:
                    self.logger.warn("{} Pitches can't init. because {}".format(note.num.value,
                                                                                traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("PBStart"):
                try:
                    note.pbStart.init(line.replace("PBStart=", ""))
                except Exception as e:
                    self.logger.warn("{} PBStart can't init. because {}".format(note.num.value,
                                                                                traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("PBS"):
                try:
                    note.pbs.init(line.replace("PBS=", ""))
                except Exception as e:
                    self.logger.warn("{} PBS can't init. because {}".format(note.num.value,
                                                                            traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("PBY"):
                try:
                    note.pby.init(line.replace("PBY=", ""))
                except Exception as e:
                    self.logger.warn("{} PBY can't init. because {}".format(note.num.value,
                                                                            traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("PBM"):
                try:
                    note.pbm.init(line.replace("PBM=", ""))
                except Exception as e:
                    self.logger.warn("{} PBM can't init. because {}".format(note.num.value,
                                                                            traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("PBW"):
                try:
                    note.pbw.init(line.replace("PBW=", ""))
                except Exception as e:
                    self.logger.warn("{} PBW can't init. because {}".format(note.num.value,
                                                                            traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("Flags"):
                try:
                    note.flags.init(line.replace("Flags=", ""))
                except Exception as e:
                    self.logger.warn("{} Flags can't init. because {}".format(note.num.value,
                                                                              traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("VBR"):
                try:
                    note.vibrato.init(line.replace("VBR=", ""))
                except Exception as e:
                    self.logger.warn("{} VBR can't init. because {}".format(note.num.value,
                                                                            traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("Envelope"):
                try:
                    note.envelope.init(line.replace("Envelope=", ""))
                except Exception as e:
                    self.logger.warn("{} Envelope can't init. because {}".format(note.num.value,
                                                                                 traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("Label"):
                try:
                    note.label.init(line.replace("Label=", ""))
                except Exception as e:
                    self.logger.warn("{} Label can't init. because {}".format(note.num.value,
                                                                              traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("$direct"):
                try:
                    note.direct.init(line.replace("$direct=", ""))
                except Exception as e:
                    self.logger.warn("{} $direct can't init. because {}".format(note.num.value,
                                                                                traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("$region"):
                try:
                    note.region.init(line.replace("$region=", ""))
                except Exception as e:
                    self.logger.warn("{} $region can't init. because {}".format(note.num.value,
                                                                                traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("$region_end"):
                try:
                    note.region_end.init(line.replace("$region_end=", ""))
                except Exception as e:
                    self.logger.warn("{} $region_end can't init. because {}".format(note.num.value,
                                                                                    traceback.format_exception_only(type(e), e)[0].rstrip('\n')))

    def save(self, filepath: str = "", encoding: str = "cp932"):
        '''
        | self.filepathもしくはfilepathにファイルを保存します。
        | windows版UTAUとの互換性を優先してcp932を優先します。

        Parameters
        ----------
        filepath: str, default ""
        encoding: str, default "cp932"
        '''
        if filepath != "":
            self.filepath = filepath
        os.makedirs(os.path.split(self.filepath)[0], exist_ok=True)
        self.logger.info("saving ust to:{}".format(self.filepath))
        with open(self.filepath, "w", encoding=encoding) as fw:
            fw.write("[#VERSION]\r\n")
            fw.write("UST Version{:.1f}\r\n".format(self.version))
            fw.write("[#SETTING]\r\n")
            fw.write("Tempo={:.2f}\r\n".format(self.tempo))
            fw.write("Tracks=1\r\n")
            fw.write("ProjectName={}\r\n".format(self.project_name))
            fw.write("VoiceDir={}\r\n".format(self.voice_dir))
            fw.write("OutFile={}\r\n".format(self.output_file))
            fw.write("CacheDir={}\r\n".format(self.cache_dir))
            fw.write("Tool1={}\r\n".format(self.wavtool))
            fw.write("Tool2={}\r\n".format(self.resamp))
            fw.write("Mode2={}\r\n".format(self.mode2))
            for note in self.notes:
                fw.write("[#{}]\r\n".format(note.num.value))
                fw.write("Length={}\r\n".format(note.length.value))
                fw.write("Lyric={}\r\n".format(note.lyric.value))
                fw.write("NoteNum={}\r\n".format(note.notenum.value))
                if note.tempo.hasValue:
                    fw.write("Tempo={}\r\n".format(note.tempo.value))
                if note.pre.hasValue:
                    fw.write("PreUtterance={}\r\n".format(note.pre.value))
                if note.ove.hasValue:
                    fw.write("VoiceOverlap={}\r\n".format(note.ove.value))
                if note.stp.hasValue:
                    fw.write("StartPoint={}\r\n".format(note.stp.value))
                if note.velocity.hasValue:
                    fw.write("Velocity={}\r\n".format(note.velocity.value))
                if note.intensity.hasValue:
                    fw.write("Intensity={}\r\n".format(note.intensity.value))
                if note.modulation.hasValue:
                    fw.write("Modulation={}\r\n".format(note.modulation.value))
                if note.pitches.hasValue:
                    fw.write("Pitches={}\r\n".format(note.pitches.value))
                if note.pbStart.hasValue:
                    fw.write("PBStart={}\r\n".format(note.pbStart.value))
                if note.pbs.hasValue:
                    fw.write("PBS={}\r\n".format(note.pbs.value))
                if note.pby.hasValue:
                    fw.write("PBY={}\r\n".format(note.pby.value))
                if note.pbm.hasValue:
                    fw.write("PBM={}\r\n".format(note.pbm.value))
                if note.pbw.hasValue:
                    fw.write("PBW={}\r\n".format(note.pbw.value))
                if note.flags.hasValue:
                    fw.write("Flags={}\r\n".format(note.flags.value))
                if note.vibrato.hasValue:
                    fw.write("VBR={}\r\n".format(note.vibrato.value))
                if note.envelope.hasValue:
                    fw.write("Envelope={}\r\n".format(note.envelope.value))
                if note.label.hasValue:
                    fw.write("Label={}\r\n".format(note.label.value))
                if note.direct.hasValue:
                    fw.write("$direct={}\r\n".format(note.direct.value))
                if note.region.hasValue:
                    fw.write("$region={}\r\n".format(note.region.value))
                if note.region_end.hasValue:
                    fw.write("$region_end={}\r\n".format(note.region_end.value))
            fw.write("[#TRACKEND]\r\n")
        self.logger.info("saving ust to:{} complete".format(self.filepath))
