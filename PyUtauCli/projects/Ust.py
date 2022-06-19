import os
import os.path
import locale
import traceback
from logging import Logger

from .Note import Note
import settings.logger as mylogger


default_logger = mylogger.get_logger(__name__, False)


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
    project_name: str = ""
    voice_dir: str = ""
    cache_dir: str = ""
    output_file: str = ""
    tempo: float = 120.0
    wavtool: str = ""
    resamp: str = ""
    flags: str = ""
    mode2: bool = False
    utf8: bool = False
    notes: list = []

    @property
    def version(self) -> float:
        return self._version

    def __init__(self, filepath: str, *, logger: Logger = None):
        self.logger = logger or default_logger
        self.filepath = filepath
        self.notes = []

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
        with open(self.filepath, "rb") as fr:
            data = fr.read()
        seek: int = self._load_header(data)
        self.logger.info("loading header complete.")
        self._load_note(data[seek:])
        self.logger.info("loading note complete.notes:{}".format(len(self.notes)))
        for i in range(len(self.notes)):
            if i != 0:
                self.notes[i].prev = self.notes[i - 1]
                self.notes[i - 1].next = self.notes[i]

    def _load_header(self, data: bytes) -> int:
        '''
        | dataをシステムの文字コードもしくはcp932でデコードを試み、各パラメータを更新します。

        Parameters
        ----------
        data: byte
            self.filepathをバイナリで読み込んだもの

        Returns
        -------
        cursor: int
            ヘッダ末尾の位置

        Raises
        ------
        UnicodeDecodeError
            ファイルがシステム既定でもcp932でもデコードできなかった場合
        '''
        version_cursor: int = data.find(b"[#VERSION]")
        setting_cursor: int = data.find(b"[#SETTING]")
        cursor: int = 0
        header_lines: list
        if (setting_cursor == -1 and version_cursor == -1):
            setting_cursor = 0
        cursor = data[setting_cursor + 1:].find(b"[#")
        cursor += setting_cursor
        try:
            header_lines = data[:cursor].decode(locale.getlocale()[1]).replace("\r", "").split("\n")
        except:
            try:
                header_lines = data[:cursor].decode("cp932").replace("\r", "").split("\n")
            except UnicodeDecodeError as e:
                self.logger.error("can't read {}'s header. because required character encoding is system default or cp932".format(self.filepath))
                e.reason = "can't read {}'s header. because required character encoding is system default or cp932".format(self.filepath)
                raise e
        self._load_head_helper(header_lines)
        return cursor

    def _load_head_helper(self, lines):
        vflag: bool = False
        for line in lines:
            if line == "[#VERSION]":
                vflag = True
            elif vflag:
                vflag = False
                self._version = float(line.replace("UST Version", ""))
            elif line.startswith("Tempo="):
                self.tempo = float(line.replace("Tempo=", ""))
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

    def _load_note(self, data: bytes):
        '''
        | dataをcp932もしくはutf-8読み込み、各ノートのパラメータを更新します。

        Parameters
        ----------
        data: byte
            self.filepathをバイナリで読み込み、ヘッダ部分を除いたもの

        Raises
        ------
        UnicodeDecodeError
            ファイルがcp932でもutf-8でも開けなかった場合
        '''
        lines: list = []
        try:
            lines = data.decode("cp932").replace("\r", "").split("\n")
        except:
            try:
                lines = data.decode("utf-8").replace("\r", "").split("\n")
            except UnicodeDecodeError as e:
                self.logger.error("can't read {}'s body. because required character encoding is cp932 or utf-8".format(self.filepath))
                e.reason = "can't read {}'s body. because required character encoding is cp932 or utf-8".format(self.filepath)
                raise e
        self._load_note_helper(lines)

    def _load_note_helper(self, lines: list):
        tempo: float = self.tempo
        note: Note = None
        for line in lines:
            if line == "[#TRACKEND]":
                continue
            elif line.startswith("[#"):
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
                    tempo = note.tempo.value
                except Exception as e:
                    self.logger.warn("{} tempo can't init. because {}".format(note.num.value,
                                                                              traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("PreUtterance"):
                try:
                    if line.replace("PreUtterance=", "") != "":
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
            elif line.startswith("PitchBend="):
                try:
                    note.pitches.init_from_str(line.replace("PitchBend=", ""))
                except Exception as e:
                    self.logger.warn("{} PitchBend can't init. because {}".format(note.num.value,
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
                    note.pby.init_from_str(line.replace("PBY=", ""))
                except Exception as e:
                    self.logger.warn("{} PBY can't init. because {}".format(note.num.value,
                                                                            traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("PBM"):
                try:
                    note.pbm.init_from_str(line.replace("PBM=", ""))
                except Exception as e:
                    self.logger.warn("{} PBM can't init. because {}".format(note.num.value,
                                                                            traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("PBW"):
                try:
                    note.pbw.init_from_str(line.replace("PBW=", ""))
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
            elif line.startswith("$region="):
                try:
                    note.region.init(line.replace("$region=", ""))
                except Exception as e:
                    self.logger.warn("{} $region can't init. because {}".format(note.num.value,
                                                                                traceback.format_exception_only(type(e), e)[0].rstrip('\n')))
            elif line.startswith("$region_end="):
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
        if os.path.split(self.filepath)[0] != "":
            os.makedirs(os.path.split(self.filepath)[0], exist_ok=True)
        self.logger.info("saving ust to:{}".format(self.filepath))
        with open(self.filepath, "w", encoding=encoding) as fw:
            fw.write("[#VERSION]\n")
            fw.write("UST Version{:.1f}\n".format(self.version))
            fw.write("[#SETTING]\n")
            fw.write("Tempo={:.2f}\n".format(self.tempo))
            fw.write("Tracks=1\n")
            fw.write("Project={}\n".format(self.project_name))
            fw.write("VoiceDir={}\n".format(self.voice_dir))
            fw.write("OutFile={}\n".format(self.output_file))
            fw.write("CacheDir={}\n".format(self.cache_dir))
            fw.write("Tool1={}\n".format(self.wavtool))
            fw.write("Tool2={}\n".format(self.resamp))
            fw.write("Flags={}\n".format(self.flags))
            fw.write("Mode2={}\n".format(self.mode2))
            for note in self.notes:
                fw.write("[{}]\n".format(str(note.num)))
                fw.write("Length={}\n".format(str(note.length)))
                fw.write("Lyric={}\n".format(str(note.lyric)))
                fw.write("NoteNum={}\n".format(str(note.notenum.value)))
                if note.tempo.hasValue:
                    fw.write("Tempo={}\n".format(str(note.tempo)))
                if note.pre.hasValue:
                    fw.write("PreUtterance={}\n".format(str(note.pre)))
                else:
                    fw.write("PreUtterance=\n")
                if note.ove.hasValue:
                    fw.write("VoiceOverlap={}\n".format(str(note.ove)))
                if note.stp.hasValue:
                    fw.write("StartPoint={}\n".format(str(note.stp)))
                if note.velocity.hasValue:
                    fw.write("Velocity={}\n".format(str(note.velocity)))
                if note.intensity.hasValue:
                    fw.write("Intensity={}\n".format(str(note.intensity)))
                if note.modulation.hasValue:
                    fw.write("Modulation={}\n".format(str(note.modulation)))
                if note.pitches.hasValue:
                    fw.write("PitchBend={}\n".format(str(note.pitches)))
                if note.pbStart.hasValue:
                    fw.write("PBStart={}\n".format(str(note.pbStart)))
                if note.pbs.hasValue:
                    fw.write("PBS={}\n".format(str(note.pbs)))
                if note.pby.hasValue:
                    fw.write("PBY={}\n".format(str(note.pby)))
                if note.pbm.hasValue:
                    fw.write("PBM={}\n".format(str(note.pbm)))
                if note.pbw.hasValue:
                    fw.write("PBW={}\n".format(str(note.pbw)))
                if note.flags.hasValue:
                    fw.write("Flags={}\n".format(str(note.flags)))
                if note.vibrato.hasValue:
                    fw.write("VBR={}\n".format(str(note.vibrato)))
                if note.envelope.hasValue:
                    fw.write("Envelope={}\n".format(str(note.envelope)))
                if note.label.hasValue:
                    fw.write("Label={}\n".format(str(note.label)))
                if note.direct.hasValue:
                    fw.write("$direct={}\n".format(str(note.direct)))
                if note.region.hasValue:
                    fw.write("$region={}\n".format(str(note.region)))
                if note.region_end.hasValue:
                    fw.write("$region_end={}\n".format(str(note.region_end)))
            fw.write("[#TRACKEND]\n")
        self.logger.info("saving ust to:{} complete".format(self.filepath))
