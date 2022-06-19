'''
| projects.Ustモジュールのテスト
| 本家UTAUの文字コードまわりが複雑で、1ファイル内に複数のエンコードを持ったファイルを読み込むなど
| 特殊なテストが必要なため、test用ファイルを生成し、読み込む方法でテストを行う。
'''

import unittest
from unittest import mock

import os
import os.path
import shutil
import logging
import locale

import projects.Ust
import settings.logger


def _make_test_ust(filename, header_encoding, body_encoding, lyric="あ", voice="音源名"):
    with open(filename, "w", encoding=header_encoding) as fw:
        fw.write("[#VERSION]\n")
        fw.write("UST Version1.2\n")
        fw.write("[#SETTING]\n")
        fw.write("Tempo=150.00\n")
        fw.write("Tracks=1\n")
        fw.write("Project=test\n")
        fw.write("VoiceDir=%VOICE%{}\n".format(voice))
        fw.write("OutFile=output.wav\n")
        fw.write("CacheDir=main__.cache\n")
        fw.write("Tool1=wavtool.exe\n")
        fw.write("Tool2=resamp.exe\n")
        fw.write("Flags=B50\n")
        fw.write("Mode2=True\n")

    with open(filename, "a", encoding=body_encoding) as fw:
        fw.write("[#0000]\n")
        fw.write("Length=1920\n")
        fw.write("Lyric={}\n".format(lyric))
        fw.write("NoteNum=60\n")
        fw.write("PreUtterance=\n")


class TestUstInputEncoding(unittest.TestCase):
    def setUp(self):
        if os.path.isdir(os.path.join("testdata", "ust")):
            shutil.rmtree(os.path.join("testdata", "ust"))
        os.makedirs(os.path.join("testdata", "ust"), exist_ok=True)
        _make_test_ust(os.path.join("testdata", "ust", "cp932-cp932.ust"), "cp932", "cp932")
        _make_test_ust(os.path.join("testdata", "ust", "cp932-utf8.ust"), "cp932", "utf-8")
        _make_test_ust(os.path.join("testdata", "ust", "cp932-cp950.ust"), "cp932", "cp950", lyric=b"\xf0\xfe".decode("cp950"))
        _make_test_ust(os.path.join("testdata", "ust", "cp950-cp932.ust"), "cp950", "cp932", voice=b"\xf0\xfe".decode("cp950"))
        _make_test_ust(os.path.join("testdata", "ust", "cp950-utf8.ust"), "cp950", "utf-8", voice=b"\xf0\xfe".decode("cp950"))
        _make_test_ust(os.path.join("testdata", "ust", "utf8-cp932.ust"), "utf-8", "cp932", voice="音源")
        _make_test_ust(os.path.join("testdata", "ust", "utf8-utf8.ust"), "utf-8", "utf-8", voice="音源", lyric="音源")
        self.test_logger = settings.logger.get_logger("TEST", True)

    def test_init(self):
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp932-cp932.ust"))
        self.assertEqual(ust.filepath, os.path.join("testdata", "ust", "cp932-cp932.ust"))
        self.assertEqual(ust.version, 1.2)
        self.assertFalse(ust.mode2)

    def test_load_not_found_file(self):
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp932-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(FileNotFoundError) as cm:
                ust.load(os.path.join("testdata", "ust", "notfound.ust"))
        self.assertEqual(cm.exception.args[0], "{} is not found".format(ust.filepath))
        self.assertEqual(logcm.output[0], "ERROR:TEST:{} is not found".format(ust.filepath))

    def test_load_cp932_injapan_win(self):
        locale.setlocale(locale.LC_CTYPE, "japanese")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp932-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(ust.tempo, 150)
        self.assertEqual(ust.project_name, "test")
        self.assertEqual(ust.voice_dir, "%VOICE%音源名")
        self.assertEqual(ust.output_file, "output.wav")
        self.assertEqual(ust.cache_dir, "main__.cache")
        self.assertEqual(ust.wavtool, "wavtool.exe")
        self.assertEqual(ust.resamp, "resamp.exe")
        self.assertEqual(ust.flags, "B50")
        self.assertEqual(logcm.output[2], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))

    def test_load_cp932_injapan_utf8(self):
        locale.setlocale(locale.LC_CTYPE, "ja_JP.utf8")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp932-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[2], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))

    def test_load_cp932_inother_locale(self):
        locale.setlocale(locale.LC_CTYPE, "zh_TW")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp932-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[2], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))

    def test_load_cp932_utf8_injapan_win(self):
        locale.setlocale(locale.LC_CTYPE, "japanese")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp932-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[2], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))

    def test_load_cp932_utf8_injapan_utf8(self):
        locale.setlocale(locale.LC_CTYPE, "ja_JP.utf8")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp932-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[2], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))

    def test_load_cp932_utf8_inother_locale(self):
        locale.setlocale(locale.LC_CTYPE, "zh_TW")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp932-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[2], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))

    def test_load_cp932_otherlocale_injapan_win(self):
        locale.setlocale(locale.LC_CTYPE, "japanese")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp932-cp950.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s body. because required character encoding is cp932 or utf-8".format(ust.filepath))
        self.assertEqual(logcm.output[2], "ERROR:TEST:can't read {}'s body. because required character encoding is cp932 or utf-8".format(ust.filepath))

    def test_load_cp932_otherlocale_injapan_utf8(self):
        locale.setlocale(locale.LC_CTYPE, "ja_JP.utf8")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp932-cp950.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s body. because required character encoding is cp932 or utf-8".format(ust.filepath))
        self.assertEqual(logcm.output[2], "ERROR:TEST:can't read {}'s body. because required character encoding is cp932 or utf-8".format(ust.filepath))

    def test_load_cp932_otherlocale_inother_locale(self):
        locale.setlocale(locale.LC_CTYPE, "zh_TW")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp932-cp950.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s body. because required character encoding is cp932 or utf-8".format(ust.filepath))
        self.assertEqual(logcm.output[2], "ERROR:TEST:can't read {}'s body. because required character encoding is cp932 or utf-8".format(ust.filepath))

    def test_load_otherlocale_cp932_injapan_win(self):
        locale.setlocale(locale.LC_CTYPE, "japanese")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp950-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(
            logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))

    def test_load_otherlocale_cp932_injapan_utf8(self):
        locale.setlocale(locale.LC_CTYPE, "ja_JP.utf8")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp950-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(
            logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))

    def test_load_otherlocale_cp932_inother_locale(self):
        locale.setlocale(locale.LC_CTYPE, "zh_TW")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp950-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[2], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))

    def test_load_otherlocale_utf8_injapan_win(self):
        locale.setlocale(locale.LC_CTYPE, "japanese")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp950-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(
            logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))

    def test_load_otherlocale_utf8_injapan_utf8(self):
        locale.setlocale(locale.LC_CTYPE, "ja_JP.utf8")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp950-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(
            logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))

    def test_load_otherlocale_utf8_inother_locale(self):
        locale.setlocale(locale.LC_CTYPE, "zh_TW")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "cp950-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[2], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))

    def test_load_utf8_cp932_injapan_win(self):
        locale.setlocale(locale.LC_CTYPE, "japanese")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "utf8-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(
            logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))

    def test_load_utf8_cp932_injapan_utf8(self):
        locale.setlocale(locale.LC_CTYPE, "ja_JP.utf8")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "utf8-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[2], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))

    def test_load_utf8_cp932_inother_locale(self):
        locale.setlocale(locale.LC_CTYPE, "zh_TW")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "utf8-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(
            logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))

    def test_load_utf8_utf8_injapan_win(self):
        locale.setlocale(locale.LC_CTYPE, "japanese")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "utf8-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(
            logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))

    def test_load_utf8_utf8_injapan_utf8(self):
        locale.setlocale(locale.LC_CTYPE, "ja_JP.utf8")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "utf8-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[2], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))

    def test_load_utf8_utf8_inother_locale(self):
        locale.setlocale(locale.LC_CTYPE, "zh_TW")
        ust = projects.Ust.Ust(os.path.join("testdata", "ust", "utf8-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(
            logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))

    def tearDown(self):
        if os.path.isdir(os.path.join("testdata")):
            shutil.rmtree(os.path.join("testdata"))


class TestLoadHeader(unittest.TestCase):
    def setUp(self):
        self.ust = projects.Ust.Ust("testpath")

    def test_simple(self):
        test_header = ["[#VERSION]",
                       "UST Version1.2",
                       "[#SETTING]",
                       "Tempo=150.00",
                       "Tracks=1",
                       "Project=test",
                       "VoiceDir=%VOICE%{}".format("aaa"),
                       "OutFile=output.wav",
                       "CacheDir=main__.cache",
                       "Tool1=wavtool.exe",
                       "Tool2=resamp.exe",
                       "Flags=B50",
                       "Mode2=True"]
        test_note = ["[#0000]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance=",
                     "[#0001]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance="]
        data = "\n".join(test_header + test_note).encode("cp932")
        header = "\n".join(test_header).encode("cp932")
        cursor = self.ust._load_header(data)
        self.assertEqual(cursor, len(header))
        self.assertEqual(self.ust.tempo, 150)
        self.assertEqual(self.ust.project_name, "test")
        self.assertEqual(self.ust.voice_dir, "%VOICE%aaa")
        self.assertEqual(self.ust.output_file, "output.wav")
        self.assertEqual(self.ust.cache_dir, "main__.cache")
        self.assertEqual(self.ust.wavtool, "wavtool.exe")
        self.assertEqual(self.ust.resamp, "resamp.exe")
        self.assertEqual(self.ust.flags, "B50")
        self.assertTrue(self.ust.mode2)

    def test_no_version(self):
        test_header = ["[#SETTING]",
                       "Tempo=150.00",
                       "Tracks=1",
                       "Project=test",
                       "VoiceDir=%VOICE%{}".format("aaa"),
                       "OutFile=output.wav",
                       "CacheDir=main__.cache",
                       "Tool1=wavtool.exe",
                       "Tool2=resamp.exe",
                       "Flags=B50",
                       "Mode2=True"]
        test_note = ["[#0000]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance=",
                     "[#0001]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance="]
        data = "\n".join(test_header + test_note).encode("cp932")
        header = "\n".join(test_header).encode("cp932")
        cursor = self.ust._load_header(data)
        self.assertEqual(cursor, len(header))
        self.assertEqual(self.ust.tempo, 150)
        self.assertEqual(self.ust.project_name, "test")
        self.assertEqual(self.ust.voice_dir, "%VOICE%aaa")
        self.assertEqual(self.ust.output_file, "output.wav")
        self.assertEqual(self.ust.cache_dir, "main__.cache")
        self.assertEqual(self.ust.wavtool, "wavtool.exe")
        self.assertEqual(self.ust.resamp, "resamp.exe")
        self.assertEqual(self.ust.flags, "B50")
        self.assertTrue(self.ust.mode2)

    def test_no_setting(self):
        test_header = ["[#VERSION]",
                       "UST Version1.2"]
        test_note = ["[#0000]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance=",
                     "[#0001]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance="]
        data = "\n".join(test_header + test_note).encode("cp932")
        header = "\n".join(test_header).encode("cp932")
        cursor = self.ust._load_header(data)

    def test_no_header(self):
        test_header = []
        test_note = ["[#0000]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance=",
                     "[#0001]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance="]
        data = "\n".join(test_header + test_note).encode("cp932")
        header = "\n".join(test_header).encode("cp932")
        cursor = self.ust._load_header(data)

    def test_simple_start_prev(self):
        test_header = ["[#VERSION]",
                       "UST Version1.2",
                       "[#SETTING]",
                       "Tempo=150.00",
                       "Tracks=1",
                       "Project=test",
                       "VoiceDir=%VOICE%{}".format("aaa"),
                       "OutFile=output.wav",
                       "CacheDir=main__.cache",
                       "Tool1=wavtool.exe",
                       "Tool2=resamp.exe",
                       "Flags=B50",
                       "Mode2=True"]
        test_note = ["[#PREV]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance=",
                     "[#0001]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance="]
        data = "\n".join(test_header + test_note).encode("cp932")
        header = "\n".join(test_header).encode("cp932")
        cursor = self.ust._load_header(data)
        self.assertEqual(cursor, len(header))
        self.assertEqual(self.ust.tempo, 150)
        self.assertEqual(self.ust.project_name, "test")
        self.assertEqual(self.ust.voice_dir, "%VOICE%aaa")
        self.assertEqual(self.ust.output_file, "output.wav")
        self.assertEqual(self.ust.cache_dir, "main__.cache")
        self.assertEqual(self.ust.wavtool, "wavtool.exe")
        self.assertEqual(self.ust.resamp, "resamp.exe")
        self.assertEqual(self.ust.flags, "B50")
        self.assertTrue(self.ust.mode2)

    def test_simple_start_delete(self):
        test_header = ["[#VERSION]",
                       "UST Version1.2",
                       "[#SETTING]",
                       "Tempo=150.00",
                       "Tracks=1",
                       "Project=test",
                       "VoiceDir=%VOICE%{}".format("aaa"),
                       "OutFile=output.wav",
                       "CacheDir=main__.cache",
                       "Tool1=wavtool.exe",
                       "Tool2=resamp.exe",
                       "Flags=B50",
                       "Mode2=True"]
        test_note = ["[#DELETE]"
                     "[#0001]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance="]
        data = "\n".join(test_header + test_note).encode("cp932")
        header = "\n".join(test_header).encode("cp932")
        cursor = self.ust._load_header(data)
        self.assertEqual(cursor, len(header))
        self.assertEqual(self.ust.tempo, 150)
        self.assertEqual(self.ust.project_name, "test")
        self.assertEqual(self.ust.voice_dir, "%VOICE%aaa")
        self.assertEqual(self.ust.output_file, "output.wav")
        self.assertEqual(self.ust.cache_dir, "main__.cache")
        self.assertEqual(self.ust.wavtool, "wavtool.exe")
        self.assertEqual(self.ust.resamp, "resamp.exe")
        self.assertEqual(self.ust.flags, "B50")
        self.assertTrue(self.ust.mode2)

    def test_simple_start_insert(self):
        test_header = ["[#VERSION]",
                       "UST Version1.2",
                       "[#SETTING]",
                       "Tempo=150.00",
                       "Tracks=1",
                       "Project=test",
                       "VoiceDir=%VOICE%{}".format("aaa"),
                       "OutFile=output.wav",
                       "CacheDir=main__.cache",
                       "Tool1=wavtool.exe",
                       "Tool2=resamp.exe",
                       "Flags=B50",
                       "Mode2=True"]
        test_note = ["[#INSERT]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance=",
                     "[#0001]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance="]
        data = "\n".join(test_header + test_note).encode("cp932")
        header = "\n".join(test_header).encode("cp932")
        cursor = self.ust._load_header(data)
        self.assertEqual(cursor, len(header))
        self.assertEqual(self.ust.tempo, 150)
        self.assertEqual(self.ust.project_name, "test")
        self.assertEqual(self.ust.voice_dir, "%VOICE%aaa")
        self.assertEqual(self.ust.output_file, "output.wav")
        self.assertEqual(self.ust.cache_dir, "main__.cache")
        self.assertEqual(self.ust.wavtool, "wavtool.exe")
        self.assertEqual(self.ust.resamp, "resamp.exe")
        self.assertEqual(self.ust.flags, "B50")
        self.assertTrue(self.ust.mode2)


class TestLoadNote(unittest.TestCase):
    def setUp(self):
        self.test_logger = settings.logger.get_logger("TEST", True)
        self.ust = projects.Ust.Ust("testpath", logger=self.test_logger)
        self.ust.tempo = 150
        self.ust.flags = "B50"

    def test_minimum_note(self):
        test_note = ["[#0000]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance="]
        data = "\n".join(test_note + ["[#TRACKEND]"]).encode("cp932")
        self.ust._load_note(data)
        self.assertEqual(len(self.ust.notes), 1)
        self.assertEqual(self.ust.notes[0].num.value, "#0000")
        self.assertEqual(self.ust.notes[0].length.value, 1920)
        self.assertEqual(self.ust.notes[0].lyric.value, "あ")
        self.assertEqual(self.ust.notes[0].notenum.value, 60)
        self.assertEqual(self.ust.notes[0].tempo.value, 150)
        self.assertFalse(self.ust.notes[0].tempo.hasValue)
        self.assertEqual(self.ust.notes[0].flags.value, "B50")
        self.assertFalse(self.ust.notes[0].flags.hasValue)

    def test_fully_note(self):
        test_note = ["[#0000]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "Tempo=120",
                     "PreUtterance=1",
                     "@preuttr=2",
                     "VoiceOverlap=3",
                     "@overlap=4",
                     "StartPoint=5",
                     "@stpoint=6",
                     "@filename=filepath",
                     "@alias=あ_C4",
                     "Velocity=150",
                     "Intensity=80",
                     "Modulation=30",
                     "PitchBend=0,1,2,3",
                     "PBStart=-10.0",
                     "PBS=-5;3",
                     "PBY=1,2,3",
                     "PBW=10,20,30,40",
                     "PBM=,s,r,j,",
                     "Flags=g-5",
                     "VBR=1,2,3,4,5,6,7,8",
                     "Envelope=9,10,11,12,13,14,15,%,16,17,18",
                     "Label=aa",
                     "$direct=True",
                     "$region=1番",
                     "$region_end=イントロ",
                     ]
        data = "\n".join(test_note + ["[#TRACKEND]"]).encode("cp932")
        self.ust._load_note(data)
        self.assertEqual(len(self.ust.notes), 1)
        self.assertEqual(self.ust.notes[0].num.value, "#0000")
        self.assertEqual(self.ust.notes[0].length.value, 1920)
        self.assertEqual(self.ust.notes[0].lyric.value, "あ")
        self.assertEqual(self.ust.notes[0].notenum.value, 60)
        self.assertEqual(self.ust.notes[0].tempo.value, 120)
        self.assertTrue(self.ust.notes[0].tempo.hasValue)
        self.assertEqual(self.ust.notes[0].pre.value, 1)
        self.assertEqual(self.ust.notes[0].atPre.value, 2)
        self.assertEqual(self.ust.notes[0].ove.value, 3)
        self.assertEqual(self.ust.notes[0].atOve.value, 4)
        self.assertEqual(self.ust.notes[0].stp.value, 5)
        self.assertEqual(self.ust.notes[0].atStp.value, 6)
        self.assertEqual(self.ust.notes[0].atFileName.value, "filepath")
        self.assertEqual(self.ust.notes[0].atAlias.value, "あ_C4")
        self.assertEqual(self.ust.notes[0].velocity.value, 150)
        self.assertEqual(self.ust.notes[0].intensity.value, 80)
        self.assertEqual(self.ust.notes[0].modulation.value, 30)
        self.assertEqual(self.ust.notes[0].pitches.value, [0, 1, 2, 3])
        self.assertEqual(self.ust.notes[0].pbStart.value, -10)
        self.assertEqual(self.ust.notes[0].pbs.time, -5)
        self.assertEqual(self.ust.notes[0].pbs.height, 3)
        self.assertEqual(self.ust.notes[0].pby.value, [1, 2, 3])
        self.assertEqual(self.ust.notes[0].pbw.value, [10, 20, 30, 40])
        self.assertEqual(self.ust.notes[0].pbm.value, ["", "s", "r", "j", ""])
        self.assertEqual(self.ust.notes[0].flags.value, "g-5")
        self.assertTrue(self.ust.notes[0].flags.hasValue)
        self.assertEqual(self.ust.notes[0].vibrato.length, 1)
        self.assertEqual(self.ust.notes[0].vibrato.cycle, 2)
        self.assertEqual(self.ust.notes[0].vibrato.depth, 3)
        self.assertEqual(self.ust.notes[0].vibrato.fadeInTime, 4)
        self.assertEqual(self.ust.notes[0].vibrato.fadeOutTime, 5)
        self.assertEqual(self.ust.notes[0].vibrato.phase, 6)
        self.assertEqual(self.ust.notes[0].vibrato.height, 7)
        self.assertEqual(self.ust.notes[0].envelope.value, "9.00,10.00,11.00,12,13,14,15,%,16.00,17.00,18")
        self.assertEqual(self.ust.notes[0].label.value, "aa")
        self.assertTrue(self.ust.notes[0].direct.value)
        self.assertEqual(self.ust.notes[0].region.value, "1番")
        self.assertEqual(self.ust.notes[0].region_end.value, "イントロ")

    def test_fully_error_note(self):
        '''
        エラーが出ることと、処理が止まらないことを確認する。
        '''
        test_note = ["[#0000]",
                     "Length=a",
                     "Lyric={}".format("あ"),
                     "NoteNum=b",
                     "Tempo=c",
                     "PreUtterance=d",
                     "@preuttr=e",
                     "VoiceOverlap=f",
                     "@overlap=g",
                     "StartPoint=h",
                     "@stpoint=i",
                     "@filename=filepath",
                     "@alias=あ_C4",
                     "Velocity=j",
                     "Intensity=k",
                     "Modulation=l",
                     "PitchBend=m",
                     "PBStart=n",
                     "PBS=o",
                     "PBY=p",
                     "PBW=q",
                     "PBM=t",
                     "Flags=g-5",
                     "VBR=r",
                     "Envelope=s",
                     "Label=aa",
                     "$direct=True",
                     "$region=1番",
                     "$region_end=イントロ",
                     ]
        data = "\n".join(test_note + ["[#TRACKEND]"]).encode("cp932")
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            self.ust._load_note(data)
        self.assertEqual(len(self.ust.notes), 1)
        self.assertEqual(self.ust.notes[0].num.value, "#0000")
        self.assertEqual(logcm.output[0], "WARNING:TEST:#0000 length can't init. because ValueError: a is not int")
        self.assertEqual(logcm.output[1], "WARNING:TEST:#0000 notenum can't init. because ValueError: b is not int")
        self.assertEqual(logcm.output[2], "WARNING:TEST:#0000 tempo can't init. because ValueError: c is not float")
        self.assertEqual(self.ust.notes[0].tempo.value, 150)
        self.assertFalse(self.ust.notes[0].tempo.hasValue)
        self.assertEqual(logcm.output[3], "WARNING:TEST:#0000 pre can't init. because ValueError: d is not float")
        self.assertEqual(logcm.output[4], "WARNING:TEST:#0000 @preuttr can't init. because ValueError: e is not float")
        self.assertEqual(logcm.output[5], "WARNING:TEST:#0000 ove can't init. because ValueError: f is not float")
        self.assertEqual(logcm.output[6], "WARNING:TEST:#0000 @overlap can't init. because ValueError: g is not float")
        self.assertEqual(logcm.output[7], "WARNING:TEST:#0000 stp can't init. because ValueError: h is not float")
        self.assertEqual(logcm.output[8], "WARNING:TEST:#0000 @stpoint can't init. because ValueError: i is not float")
        self.assertEqual(logcm.output[9], "WARNING:TEST:#0000 Velocity can't init. because ValueError: j is not int")
        self.assertEqual(logcm.output[10], "WARNING:TEST:#0000 Intensity can't init. because ValueError: k is not int")
        self.assertEqual(logcm.output[11], "WARNING:TEST:#0000 Modulation can't init. because ValueError: l is not int")
        self.assertEqual(logcm.output[12], "WARNING:TEST:#0000 PitchBend can't init. because ValueError: m is not int")
        self.assertEqual(logcm.output[13], "WARNING:TEST:#0000 PBStart can't init. because ValueError: n is not float")
        self.assertEqual(logcm.output[14], "WARNING:TEST:#0000 PBS can't init. because ValueError: o is not float")
        self.assertEqual(logcm.output[15], "WARNING:TEST:#0000 PBY can't init. because ValueError: p is not float")
        self.assertEqual(logcm.output[16], "WARNING:TEST:#0000 PBW can't init. because ValueError: q is not float")
        self.assertEqual(logcm.output[17], "WARNING:TEST:#0000 PBM can't init. because ValueError: t is not '',s,r,j")
        self.assertEqual(logcm.output[18], "WARNING:TEST:#0000 VBR can't init. because ValueError: r is not float")
        self.assertEqual(logcm.output[19], "WARNING:TEST:#0000 Envelope can't init. because ValueError: s is not envelope pattern")
        self.assertEqual(len(logcm.output), 20)

    def test_3notes(self):
        test_note = ["[#0000]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance="]
        test_note2 = ["[#0001]",
                      "Length=1920",
                      "Lyric={}".format("あ"),
                      "NoteNum=60",
                      "Tempo=120",
                      "PreUtterance=1",
                      "@preuttr=2",
                      "VoiceOverlap=3",
                      "@overlap=4",
                      "StartPoint=5",
                      "@stpoint=6",
                      "@filename=filepath",
                      "@alias=あ_C4",
                      "Velocity=150",
                      "Intensity=80",
                      "Modulation=30",
                      "PitchBend=0,1,2,3",
                      "PBStart=-10.0",
                      "PBS=-5;3",
                      "PBY=1,2,3",
                      "PBW=10,20,30,40",
                      "PBM=,s,r,j,",
                      "Flags=g-5",
                      "VBR=1,2,3,4,5,6,7,8",
                      "Envelope=9,10,11,12,13,14,15,%,16,17,18",
                      "Label=aa",
                      "$direct=True",
                      "$region=1番",
                      "$region_end=イントロ",
                      ]
        test_note3 = ["[#0002]",
                      "Length=1920",
                      "Lyric={}".format("あ"),
                      "NoteNum=60",
                      "PreUtterance="]
        data = "\n".join(test_note + test_note2 + test_note3 + ["[#TRACKEND]"]).encode("cp932")
        self.ust._load_note(data)
        self.assertEqual(len(self.ust.notes), 3)
        self.assertEqual(self.ust.notes[0].num.value, "#0000")
        self.assertEqual(self.ust.notes[0].length.value, 1920)
        self.assertEqual(self.ust.notes[0].lyric.value, "あ")
        self.assertEqual(self.ust.notes[0].notenum.value, 60)
        self.assertEqual(self.ust.notes[0].tempo.value, 150)
        self.assertFalse(self.ust.notes[0].tempo.hasValue)
        self.assertEqual(self.ust.notes[0].flags.value, "B50")
        self.assertFalse(self.ust.notes[0].flags.hasValue)
        self.assertEqual(self.ust.notes[1].num.value, "#0001")
        self.assertEqual(self.ust.notes[1].length.value, 1920)
        self.assertEqual(self.ust.notes[1].lyric.value, "あ")
        self.assertEqual(self.ust.notes[1].notenum.value, 60)
        self.assertEqual(self.ust.notes[1].tempo.value, 120)
        self.assertTrue(self.ust.notes[1].tempo.hasValue)
        self.assertEqual(self.ust.notes[1].pre.value, 1)
        self.assertEqual(self.ust.notes[1].atPre.value, 2)
        self.assertEqual(self.ust.notes[1].ove.value, 3)
        self.assertEqual(self.ust.notes[1].atOve.value, 4)
        self.assertEqual(self.ust.notes[1].stp.value, 5)
        self.assertEqual(self.ust.notes[1].atStp.value, 6)
        self.assertEqual(self.ust.notes[1].atFileName.value, "filepath")
        self.assertEqual(self.ust.notes[1].atAlias.value, "あ_C4")
        self.assertEqual(self.ust.notes[1].velocity.value, 150)
        self.assertEqual(self.ust.notes[1].intensity.value, 80)
        self.assertEqual(self.ust.notes[1].modulation.value, 30)
        self.assertEqual(self.ust.notes[1].pitches.value, [0, 1, 2, 3])
        self.assertEqual(self.ust.notes[1].pbStart.value, -10)
        self.assertEqual(self.ust.notes[1].pbs.time, -5)
        self.assertEqual(self.ust.notes[1].pbs.height, 3)
        self.assertEqual(self.ust.notes[1].pby.value, [1, 2, 3])
        self.assertEqual(self.ust.notes[1].pbw.value, [10, 20, 30, 40])
        self.assertEqual(self.ust.notes[1].pbm.value, ["", "s", "r", "j", ""])
        self.assertEqual(self.ust.notes[1].flags.value, "g-5")
        self.assertTrue(self.ust.notes[1].flags.hasValue)
        self.assertEqual(self.ust.notes[1].vibrato.length, 1)
        self.assertEqual(self.ust.notes[1].vibrato.cycle, 2)
        self.assertEqual(self.ust.notes[1].vibrato.depth, 3)
        self.assertEqual(self.ust.notes[1].vibrato.fadeInTime, 4)
        self.assertEqual(self.ust.notes[1].vibrato.fadeOutTime, 5)
        self.assertEqual(self.ust.notes[1].vibrato.phase, 6)
        self.assertEqual(self.ust.notes[1].vibrato.height, 7)
        self.assertEqual(self.ust.notes[1].envelope.value, "9.00,10.00,11.00,12,13,14,15,%,16.00,17.00,18")
        self.assertEqual(self.ust.notes[1].label.value, "aa")
        self.assertTrue(self.ust.notes[1].direct.value)
        self.assertEqual(self.ust.notes[1].region.value, "1番")
        self.assertEqual(self.ust.notes[1].region_end.value, "イントロ")
        self.assertEqual(self.ust.notes[2].num.value, "#0002")
        self.assertEqual(self.ust.notes[2].length.value, 1920)
        self.assertEqual(self.ust.notes[2].lyric.value, "あ")
        self.assertEqual(self.ust.notes[2].notenum.value, 60)
        self.assertEqual(self.ust.notes[2].tempo.value, 120)
        self.assertFalse(self.ust.notes[2].tempo.hasValue)
        self.assertEqual(self.ust.notes[2].flags.value, "B50")
        self.assertFalse(self.ust.notes[2].flags.hasValue)

class TestLoadAll(unittest.TestCase):
    @mock.patch("os.path.isfile")
    def test_write(self, mock_isfile):
        mock_isfile.return_value = True
        self.test_logger = settings.logger.get_logger("TEST", True)
        self.ust = projects.Ust.Ust("testpath", logger=self.test_logger)
        test_header = ["[#VERSION]",
                       "UST Version1.2",
                       "[#SETTING]",
                       "Tempo=150.00",
                       "Tracks=1",
                       "Project=test",
                       "VoiceDir=%VOICE%{}".format("aaa"),
                       "OutFile=output.wav",
                       "CacheDir=main__.cache",
                       "Tool1=wavtool.exe",
                       "Tool2=resamp.exe",
                       "Flags=B50",
                       "Mode2=True"]
        test_note = ["[#0000]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance="]
        test_note2 = ["[#0001]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance="]
        test_note3 = ["[#0002]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance="]
        data = "\n".join(test_header + test_note + test_note2 + test_note3 + ["[#TRACKEND]"]).encode("cp932")
        mock_io = mock.mock_open(read_data=data)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.ust.load()
                self.ust.save()
        self.assertIsNone(self.ust.notes[0].prev)
        self.assertEqual(self.ust.notes[1].prev, self.ust.notes[0])
        self.assertEqual(self.ust.notes[2].prev, self.ust.notes[1])
        self.assertIsNone(self.ust.notes[2].next)
        self.assertEqual(self.ust.notes[1].next, self.ust.notes[2])
        self.assertEqual(self.ust.notes[0].next, self.ust.notes[1])

class TestWrite(unittest.TestCase):
    @mock.patch("os.path.isfile")
    def test_write(self, mock_isfile):
        mock_isfile.return_value = True
        self.test_logger = settings.logger.get_logger("TEST", True)
        self.ust = projects.Ust.Ust("testpath", logger=self.test_logger)
        test_header = ["[#VERSION]",
                       "UST Version1.2",
                       "[#SETTING]",
                       "Tempo=150.00",
                       "Tracks=1",
                       "Project=test",
                       "VoiceDir=%VOICE%{}".format("aaa"),
                       "OutFile=output.wav",
                       "CacheDir=main__.cache",
                       "Tool1=wavtool.exe",
                       "Tool2=resamp.exe",
                       "Flags=B50",
                       "Mode2=True"]
        test_note = ["[#0000]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance="]
        test_note2 = ["[#0001]",
                      "Length=1920",
                      "Lyric={}".format("あ"),
                      "NoteNum=60",
                      "Tempo=120",
                      "PreUtterance=1",
                      "@preuttr=2",
                      "VoiceOverlap=3",
                      "@overlap=4",
                      "StartPoint=5",
                      "@stpoint=6",
                      "@filename=filepath",
                      "@alias=あ_C4",
                      "Velocity=150",
                      "Intensity=80",
                      "Modulation=30",
                      "PitchBend=0,1,2,3",
                      "PBStart=-10.0",
                      "PBS=-5;3",
                      "PBY=1,2,3",
                      "PBW=10,20,30,40",
                      "PBM=,s,r,j,",
                      "Flags=g-5",
                      "VBR=1,2,3,4,5,6,7,8",
                      "Envelope=9,10,11,12,13,14,15,%,16,17,18",
                      "Label=aa",
                      "$direct=True",
                      "$region=1番",
                      "$region_end=イントロ",
                      ]
        test_note3 = ["[#0002]",
                      "Length=1920",
                      "Lyric={}".format("あ"),
                      "NoteNum=60",
                      "PreUtterance="]
        data = "\n".join(test_header + test_note + test_note2 + test_note3 + ["[#TRACKEND]"]).encode("cp932")
        mock_io = mock.mock_open(read_data=data)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.ust.load()
                self.ust.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#VERSION]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "UST Version1.2\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "[#SETTING]\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "Tempo=150.00\n")
        self.assertEqual(mock_io().write.call_args_list[4][0][0], "Tracks=1\n")
        self.assertEqual(mock_io().write.call_args_list[5][0][0], "Project=test\n")
        self.assertEqual(mock_io().write.call_args_list[6][0][0], "VoiceDir=%VOICE%aaa\n")
        self.assertEqual(mock_io().write.call_args_list[7][0][0], "OutFile=output.wav\n")
        self.assertEqual(mock_io().write.call_args_list[8][0][0], "CacheDir=main__.cache\n")
        self.assertEqual(mock_io().write.call_args_list[9][0][0], "Tool1=wavtool.exe\n")
        self.assertEqual(mock_io().write.call_args_list[10][0][0], "Tool2=resamp.exe\n")
        self.assertEqual(mock_io().write.call_args_list[11][0][0], "Flags=B50\n")
        self.assertEqual(mock_io().write.call_args_list[12][0][0], "Mode2=True\n")
        self.assertEqual(mock_io().write.call_args_list[13][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[14][0][0], "Length=1920\n")
        self.assertEqual(mock_io().write.call_args_list[15][0][0], "Lyric=あ\n")
        self.assertEqual(mock_io().write.call_args_list[16][0][0], "NoteNum=60\n")
        self.assertEqual(mock_io().write.call_args_list[17][0][0], "PreUtterance=\n")
        self.assertEqual(mock_io().write.call_args_list[18][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[19][0][0], "Length=1920\n")
        self.assertEqual(mock_io().write.call_args_list[20][0][0], "Lyric=あ\n")
        self.assertEqual(mock_io().write.call_args_list[21][0][0], "NoteNum=60\n")
        self.assertEqual(mock_io().write.call_args_list[22][0][0], "Tempo=120.00\n")
        self.assertEqual(mock_io().write.call_args_list[23][0][0], "PreUtterance=1.000\n")
        self.assertEqual(mock_io().write.call_args_list[24][0][0], "VoiceOverlap=3.000\n")
        self.assertEqual(mock_io().write.call_args_list[25][0][0], "StartPoint=5.000\n")
        self.assertEqual(mock_io().write.call_args_list[26][0][0], "Velocity=150\n")
        self.assertEqual(mock_io().write.call_args_list[27][0][0], "Intensity=80\n")
        self.assertEqual(mock_io().write.call_args_list[28][0][0], "Modulation=30\n")
        self.assertEqual(mock_io().write.call_args_list[29][0][0], "PitchBend=0,1,2,3\n")
        self.assertEqual(mock_io().write.call_args_list[30][0][0], "PBStart=-10.000\n")
        self.assertEqual(mock_io().write.call_args_list[31][0][0], "PBS=-5;3\n")
        self.assertEqual(mock_io().write.call_args_list[32][0][0], "PBY=1.0,2.0,3.0\n")
        self.assertEqual(mock_io().write.call_args_list[33][0][0], "PBM=,s,r,j,\n")
        self.assertEqual(mock_io().write.call_args_list[34][0][0], "PBW=10.0,20.0,30.0,40.0\n")
        self.assertEqual(mock_io().write.call_args_list[35][0][0], "Flags=g-5\n")
        self.assertEqual(mock_io().write.call_args_list[36][0][0], "VBR=1.00,2.00,3.00,4.00,5.00,6.00,7.00,8.00\n")
        self.assertEqual(mock_io().write.call_args_list[37][0][0], "Envelope=9.00,10.00,11.00,12,13,14,15,%,16.00,17.00,18\n")
        self.assertEqual(mock_io().write.call_args_list[38][0][0], "Label=aa\n")
        self.assertEqual(mock_io().write.call_args_list[39][0][0], "$direct=True\n")
        self.assertEqual(mock_io().write.call_args_list[40][0][0], "$region=1番\n")
        self.assertEqual(mock_io().write.call_args_list[41][0][0], "$region_end=イントロ\n")
        self.assertEqual(mock_io().write.call_args_list[42][0][0], "[#0002]\n")
        self.assertEqual(mock_io().write.call_args_list[43][0][0], "Length=1920\n")
        self.assertEqual(mock_io().write.call_args_list[44][0][0], "Lyric=あ\n")
        self.assertEqual(mock_io().write.call_args_list[45][0][0], "NoteNum=60\n")
        self.assertEqual(mock_io().write.call_args_list[46][0][0], "PreUtterance=\n")
        self.assertEqual(mock_io().write.call_args_list[47][0][0], "[#TRACKEND]\n")
        self.assertEqual(len(logcm.output), 5)
        self.assertEqual(logcm.output[4], "INFO:TEST:saving ust to:{} complete".format(self.ust.filepath))
