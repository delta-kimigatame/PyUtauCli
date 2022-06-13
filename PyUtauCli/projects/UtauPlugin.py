import os
import os.path

from .Ust import Ust

class UtauPlugin(Ust):
    '''
    | UTAUのプラグイン用一時ファイルを扱います。
    | ほぼ、Ustと共通の仕様ですが、主に書き出しに関する仕様が異なります。
    '''
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
        self.logger.info("saving utau plugin temp to:{}".format(self.filepath))
        with open(self.filepath, "w", encoding=encoding) as fw:
            for note in self.notes:
                fw.write("[{}]\n".format(str(note.num)))
                if note.num.value == "#DELETE":
                    continue
                if note.length.hasValue and note.length.isUpdate:
                    fw.write("Length={}\n".format(str(note.length)))
                if note.lyric.hasValue and note.lyric.isUpdate:
                    fw.write("Lyric={}\n".format(str(note.lyric)))
                if note.notenum.hasValue and note.notenum.isUpdate:
                    fw.write("NoteNum={}\n".format(str(note.notenum.value)))
                if note.tempo.hasValue and note.tempo.isUpdate:
                    fw.write("Tempo={}\n".format(str(note.tempo)))
                if note.pre.hasValue and note.pre.isUpdate:
                    fw.write("PreUtterance={}\n".format(str(note.pre)))
                if note.ove.hasValue and note.ove.isUpdate:
                    fw.write("VoiceOverlap={}\n".format(str(note.ove)))
                if note.stp.hasValue and note.stp.isUpdate:
                    fw.write("StartPoint={}\n".format(str(note.stp)))
                if note.velocity.hasValue and note.velocity.isUpdate:
                    fw.write("Velocity={}\n".format(str(note.velocity)))
                if note.intensity.hasValue and note.intensity.isUpdate:
                    fw.write("Intensity={}\n".format(str(note.intensity)))
                if note.modulation.hasValue and note.modulation.isUpdate:
                    fw.write("Modulation={}\n".format(str(note.modulation)))
                if note.pitches.hasValue and note.pitches.isUpdate:
                    fw.write("Pitches={}\n".format(str(note.pitches)))
                if note.pbStart.hasValue and note.pbStart.isUpdate:
                    fw.write("PBStart={}\n".format(str(note.pbStart)))
                if note.pbs.hasValue and note.pbs.isUpdate:
                    fw.write("PBS={}\n".format(str(note.pbs)))
                if note.pby.hasValue and note.pby.isUpdate:
                    fw.write("PBY={}\n".format(str(note.pby)))
                if note.pbm.hasValue and note.pbm.isUpdate:
                    fw.write("PBM={}\n".format(str(note.pbm)))
                if note.pbw.hasValue and note.pbw.isUpdate:
                    fw.write("PBW={}\n".format(str(note.pbw)))
                if note.flags.hasValue and note.flags.isUpdate:
                    fw.write("Flags={}\n".format(str(note.flags)))
                if note.vibrato.hasValue and note.vibrato.isUpdate:
                    fw.write("VBR={}\n".format(str(note.vibrato)))
                if note.envelope.hasValue and note.envelope.isUpdate:
                    fw.write("Envelope={}\n".format(str(note.envelope)))
                if note.label.hasValue and note.label.isUpdate:
                    fw.write("Label={}\n".format(str(note.label)))
                if note.direct.hasValue and note.direct.isUpdate:
                    fw.write("$direct={}\n".format(str(note.direct)))
                if note.region.hasValue and note.region.isUpdate:
                    fw.write("$region={}\n".format(str(note.region)))
                if note.region_end.hasValue and note.region_end.isUpdate:
                    fw.write("$region_end={}\n".format(str(note.region_end)))
        self.logger.info("saving utau plugin temp to:{} complete".format(self.filepath))