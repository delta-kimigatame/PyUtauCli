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

def _make_test_ust(filename, header_encoding, body_encoding, lyric ="あ",voice="音源名"):
    with open(filename, "w", encoding = header_encoding) as fw:
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

    with open(filename, "a", encoding = body_encoding) as fw:
        fw.write("[#0000]\n")
        fw.write("Length=1920\n")
        fw.write("Lyric={}\n".format(lyric))
        fw.write("NoteNum=60\n")
        fw.write("PreUtterance=\n")

class TestUstInput(unittest.TestCase):
    def setUp(self):
        if os.path.isdir(os.path.join("testdata","ust")):
            shutil.rmtree(os.path.join("testdata","ust"))
        os.makedirs(os.path.join("testdata","ust"), exist_ok=True)
        _make_test_ust(os.path.join("testdata","ust","cp932-cp932.ust"), "cp932", "cp932")
        _make_test_ust(os.path.join("testdata","ust","cp932-utf8.ust"), "cp932", "utf-8")
        _make_test_ust(os.path.join("testdata","ust","cp932-cp950.ust"), "cp932", "cp950",lyric=b"\xf0\xfe".decode("cp950"))
        _make_test_ust(os.path.join("testdata","ust","cp950-cp932.ust"), "cp950", "cp932",voice=b"\xf0\xfe".decode("cp950"))
        _make_test_ust(os.path.join("testdata","ust","cp950-utf8.ust"), "cp950", "utf-8",voice=b"\xf0\xfe".decode("cp950"))
        _make_test_ust(os.path.join("testdata","ust","utf8-cp932.ust"), "utf-8", "cp932",voice="音源")
        _make_test_ust(os.path.join("testdata","ust","utf8-utf8.ust"), "utf-8", "utf-8",voice="音源",lyric="音源")
        self.test_logger = settings.logger.get_logger("TEST", True)

    def test_init(self):
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp932-cp932.ust"))
        self.assertEqual(ust.filepath, os.path.join("testdata","ust","cp932-cp932.ust"))
        self.assertEqual(ust.version, 1.2)
        self.assertFalse(ust.mode2)

    def test_load_not_found_file(self):
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp932-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(FileNotFoundError) as cm:
                ust.load(os.path.join("testdata","ust","notfound.ust"))
        self.assertEqual(cm.exception.args[0], "{} is not found".format(ust.filepath))
        self.assertEqual(logcm.output[0], "ERROR:TEST:{} is not found".format(ust.filepath))

    def test_load_cp932_injapan_win(self):
        locale.setlocale(locale.LC_CTYPE,"japanese")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp932-cp932.ust"), logger=self.test_logger)
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
        self.assertTrue(ust.mode2)
        self.assertEqual(logcm.output[3], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))
        
    def test_load_cp932_injapan_utf8(self):
        locale.setlocale(locale.LC_CTYPE,"ja_JP.utf8")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp932-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[3], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))
        
    def test_load_cp932_inother_locale(self):
        locale.setlocale(locale.LC_CTYPE,"zh_TW")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp932-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[3], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))
        
    def test_load_cp932_utf8_injapan_win(self):
        locale.setlocale(locale.LC_CTYPE,"japanese")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp932-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[3], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))
        
    def test_load_cp932_utf8_injapan_utf8(self):
        locale.setlocale(locale.LC_CTYPE,"ja_JP.utf8")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp932-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[3], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))
        
    def test_load_cp932_utf8_inother_locale(self):
        locale.setlocale(locale.LC_CTYPE,"zh_TW")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp932-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[3], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))

    def test_load_cp932_otherlocale_injapan_win(self):
        locale.setlocale(locale.LC_CTYPE,"japanese")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp932-cp950.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s body. because required character encoding is cp932 or utf-8".format(ust.filepath))
        self.assertEqual(logcm.output[2], "ERROR:TEST:can't read {}'s body. because required character encoding is cp932 or utf-8".format(ust.filepath))
        
    def test_load_cp932_otherlocale_injapan_utf8(self):
        locale.setlocale(locale.LC_CTYPE,"ja_JP.utf8")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp932-cp950.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s body. because required character encoding is cp932 or utf-8".format(ust.filepath))
        self.assertEqual(logcm.output[2], "ERROR:TEST:can't read {}'s body. because required character encoding is cp932 or utf-8".format(ust.filepath))
        
    def test_load_cp932_otherlocale_inother_locale(self):
        locale.setlocale(locale.LC_CTYPE,"zh_TW")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp932-cp950.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s body. because required character encoding is cp932 or utf-8".format(ust.filepath))
        self.assertEqual(logcm.output[2], "ERROR:TEST:can't read {}'s body. because required character encoding is cp932 or utf-8".format(ust.filepath))
        
    def test_load_otherlocale_cp932_injapan_win(self):
        locale.setlocale(locale.LC_CTYPE,"japanese")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp950-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))

    def test_load_otherlocale_cp932_injapan_utf8(self):
        locale.setlocale(locale.LC_CTYPE,"ja_JP.utf8")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp950-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        
    def test_load_otherlocale_cp932_inother_locale(self):
        locale.setlocale(locale.LC_CTYPE,"zh_TW")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp950-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[3], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))
        
    def test_load_otherlocale_utf8_injapan_win(self):
        locale.setlocale(locale.LC_CTYPE,"japanese")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp950-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))

    def test_load_otherlocale_utf8_injapan_utf8(self):
        locale.setlocale(locale.LC_CTYPE,"ja_JP.utf8")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp950-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        
    def test_load_otherlocale_utf8_inother_locale(self):
        locale.setlocale(locale.LC_CTYPE,"zh_TW")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","cp950-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[3], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))
        
    def test_load_utf8_cp932_injapan_win(self):
        locale.setlocale(locale.LC_CTYPE,"japanese")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","utf8-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        
    def test_load_utf8_cp932_injapan_utf8(self):
        locale.setlocale(locale.LC_CTYPE,"ja_JP.utf8")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","utf8-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[3], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))

    def test_load_utf8_cp932_inother_locale(self):
        locale.setlocale(locale.LC_CTYPE,"zh_TW")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","utf8-cp932.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        
        
    def test_load_utf8_utf8_injapan_win(self):
        locale.setlocale(locale.LC_CTYPE,"japanese")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","utf8-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
            
    def test_load_utf8_utf8_injapan_utf8(self):
        locale.setlocale(locale.LC_CTYPE,"ja_JP.utf8")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","utf8-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            ust.load()
        self.assertEqual(logcm.output[3], "INFO:TEST:loading note complete.notes:1".format(ust.filepath))

    def test_load_utf8_utf8_inother_locale(self):
        locale.setlocale(locale.LC_CTYPE,"zh_TW")
        ust = projects.Ust.Ust(os.path.join("testdata","ust","utf8-utf8.ust"), logger=self.test_logger)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with self.assertRaises(UnicodeDecodeError) as cm:
                ust.load()
        self.assertEqual(cm.exception.reason, "can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        self.assertEqual(logcm.output[1], "ERROR:TEST:can't read {}'s header. because required character encoding is system default or cp932".format(ust.filepath))
        
    def tearDown(self):
        if os.path.isdir(os.path.join("testdata")):
            shutil.rmtree(os.path.join("testdata"))
