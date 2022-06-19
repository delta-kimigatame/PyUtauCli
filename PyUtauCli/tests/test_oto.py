'''
voicebanks.otoモジュールのテスト
'''

import unittest
from unittest import mock

import os
import os.path
import wave

import voicebank.oto


class OtoRecordTest(unittest.TestCase):
    '''
    otoの各行の値に関するテスト
    '''

    def test_init(self):
        '''
        初期化に関するテスト
        '''
        oto = voicebank.oto.OtoRecord("subdir", "foo.wav", "bar", 100, 600, 200, 900, -1000)
        self.assertEqual(oto.otopath, "subdir")
        self.assertEqual(oto.filename, "foo.wav")
        self.assertEqual(oto.alias, "bar")
        self.assertEqual(oto.offset, 100)
        self.assertEqual(oto.pre, 600)
        self.assertEqual(oto.ove, 200)
        self.assertEqual(oto.consonant, 900)
        self.assertEqual(oto.blank, -1000)

    def test_init_alias_is_blank(self):
        '''
        初期化時エイリアスが""の場合
        '''
        oto = voicebank.oto.OtoRecord("subdir", "foo.wav", "", 100, 600, 200, 900, -1000)
        self.assertEqual(oto.otopath, "subdir")
        self.assertEqual(oto.filename, "foo.wav")
        self.assertEqual(oto.alias, "subdir\\foo")
        self.assertEqual(oto.offset, 100)
        self.assertEqual(oto.pre, 600)
        self.assertEqual(oto.ove, 200)
        self.assertEqual(oto.consonant, 900)
        self.assertEqual(oto.blank, -1000)

    @mock.patch("os.path.isfile")
    def test_invert_file_not_found_error(self, mock_isfile):
        '''
        invert_blank時wavファイルが見つからない場合
        '''
        mock_isfile.return_value = False
        oto = voicebank.oto.OtoRecord("subdir", "foo.wav", "bar", 100, 600, 200, 900, -1000)
        with self.assertRaises(FileNotFoundError) as cm:
            oto.invert_blank("voice")
        self.assertEqual(cm.exception.args[0], "{} is not found.".format(os.path.join("voice", "subdir", "foo.wav")))

    @mock.patch("os.path.isfile")
    def test_invert_wave_error(self, mock_isfile):
        '''
        invert_blank時指定したファイルがwavファイル出なかった場合
        '''
        mock_isfile.return_value = True
        oto = voicebank.oto.OtoRecord("subdir", "foo.wav", "bar", 100, 600, 200, 900, -1000)
        mock_io = mock.mock_open(read_data=b"test")
        with self.assertRaises(wave.Error) as cm:
            with mock.patch("wave.open", mock_io) as mocked_open:
                mocked_open.side_effect = wave.Error("file does not start with RIFF id")
                oto.invert_blank("voice")
        self.assertEqual(cm.exception.args[0], "file does not start with RIFF id")

    @mock.patch("os.path.isfile")
    def test_invert_wave(self, mock_isfile):
        '''
        invert_blank成功。元のblankが負の場合
        '''
        mock_isfile.return_value = True
        oto = voicebank.oto.OtoRecord("subdir", "foo.wav", "bar", 100, 600, 200, 900, -1000)
        mock_io = mock.MagicMock(name="open", spec=open)
        mock_io().__enter__().getnframes = mock.Mock(return_value=88200)
        mock_io().__enter__().getframerate = mock.Mock(return_value=44100)

        with mock.patch("wave.open", mock_io) as mocked_open:
            oto.invert_blank("voice")
        self.assertEqual(oto.blank, 900)

    @mock.patch("os.path.isfile")
    def test_invert_wave_positive(self, mock_isfile):
        '''
        invert_blank成功。元のblankが正の場合
        '''
        mock_isfile.return_value = True
        oto = voicebank.oto.OtoRecord("subdir", "foo.wav", "bar", 100, 600, 200, 900, 900)
        mock_io = mock.MagicMock(name="open", spec=open)
        mock_io().__enter__().getnframes = mock.Mock(return_value=88200)
        mock_io().__enter__().getframerate = mock.Mock(return_value=44100)

        with mock.patch("wave.open", mock_io) as mocked_open:
            oto.invert_blank("voice")
        self.assertEqual(oto.blank, -1000)


class OtoTest(unittest.TestCase):
    '''
    oto.iniの読み書きに関するテスト
    '''

    def test_init(self):
        '''
        | 引数無しでoto.iniを初期化する場合
        '''
        oto = voicebank.oto.Oto()
        self.assertDictEqual(oto._values, {})
        self.assertDictEqual(oto._datas_by_file, {})

    def test_setValue(self):
        '''
        _setValueに関するテスト
        '''
        oto = voicebank.oto.Oto()
        record1 = voicebank.oto.OtoRecord("subdir", "foo.wav", "bar", 100, 600, 200, 900, 900)
        record2 = voicebank.oto.OtoRecord("subdir", "foa.wav", "bar", 100, 600, 200, 900, 900)
        record3 = voicebank.oto.OtoRecord("subdir", "foa.wav", "bar", 50, 600, 200, 900, 900)
        # 初期値の設定
        oto._setValue("bar", record1)
        self.assertEqual(oto["bar"], record1)
        # 同じエイリアス、若いパス
        oto._setValue("bar", record2)
        self.assertEqual(oto["bar"], record2)
        # 同じエイリアス、老いパス
        oto._setValue("bar", record1)
        self.assertEqual(oto["bar"], record2)
        # 同じエイリアス、同じファイル、小さいオフセット
        oto._setValue("bar", record3)
        self.assertEqual(oto["bar"], record3)
        # 同じエイリアス、同じファイル、大きいオフセット
        oto._setValue("bar", record2)
        self.assertEqual(oto["bar"], record3)

    def test_load_file_unicode_decode_error(self):
        '''
        oto.iniがutf-8でもcp932でも開けなかったとき
        '''
        lines = [""]
        oto = voicebank.oto.Oto()
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with self.assertRaises(UnicodeDecodeError) as cm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                mocked_open.side_effect = UnicodeDecodeError("cp932", b"\x00\x00", 1, 2, "reason")
                oto._loadFile(os.path.join("voice", "subdir", "oto.ini"), "subdir")
        self.assertEqual(cm.exception.reason, "can't read {}. because required character encoding is utf-8 or cp932".format(os.path.join("voice", "subdir", "oto.ini")))

    def test_loadFile(self):
        '''
        oto.iniが正常に開けたとき
        '''
        lines = ["", "a", "b=1,2", "foo.wav=bar,100,600,200,900,-1000"]
        oto = voicebank.oto.Oto()
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io) as mocked_open:
            oto._loadFile(os.path.join("voice", "subdir", "oto.ini"), "subdir")

        self.assertEqual(oto._datas_by_file["subdir"][0].alias, "bar")
        self.assertEqual(len(oto._datas_by_file["subdir"]), 1)
        self.assertEqual(oto["bar"].offset, 100)
        self.assertEqual(oto["subdir\\foo"].pre, 900)
        self.assertTrue(oto.haskey("bar"))
        self.assertTrue(oto.haskey("subdir\\foo"))

    def test_load_file_unicode_decode_error_once(self):
        '''
        oto.iniがcp932で開けなかったがutf-8で開けたとき
        '''
        lines = ["", "a", "b=1,2", "foo.wav=bar,100,600,200,900,-1000"]
        oto = voicebank.oto.Oto()
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io) as mocked_open:
            mocked_open.side_effect = [UnicodeDecodeError("cp932", b"\x00\x00", 1, 2, "reason"), mock.DEFAULT]
            oto._loadFile(os.path.join("voice", "subdir", "oto.ini"), "subdir")
        self.assertEqual(oto._datas_by_file["subdir"][0].alias, "bar")
        self.assertEqual(len(oto._datas_by_file["subdir"]), 1)
        self.assertEqual(oto["bar"].offset, 100)
        self.assertEqual(oto["subdir\\foo"].pre, 900)

    @mock.patch("os.listdir")
    @mock.patch("os.path.isfile")
    def test_load_single(self, mock_isfile, mock_listdir):
        mock_isfile.return_value = True
        mock_listdir.return_value = []
        lines = ["", "a", "b=1,2", "foo.wav=bar,100,600,200,900,-1000"]
        oto = voicebank.oto.Oto()
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io) as mocked_open:
            oto.load("voice")
        self.assertEqual(oto._datas_by_file[""][0].alias, "bar")
        self.assertEqual(len(oto._datas_by_file[""]), 1)
        self.assertEqual(oto["bar"].offset, 100)
        self.assertEqual(oto["foo"].pre, 900)

    @mock.patch("os.path.isdir")
    @mock.patch("os.listdir")
    @mock.patch("os.path.isfile")
    def test_load_nest(self, mock_isfile, mock_listdir, mock_isdir):
        mock_isfile.return_value = True
        mock_listdir.return_value = ["a", "oto.ini"]
        mock_isdir.side_effect = [True, True, False, False, False, False]
        lines = ["", "a", "b=1,2", "foo.wav=bar,100,600,200,900,-1000"]
        oto = voicebank.oto.Oto()
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io) as mocked_open:
            oto.load("voice")
        self.assertEqual(oto._datas_by_file[""][0].alias, "bar")
        self.assertEqual(len(oto._datas_by_file[""]), 1)
        self.assertEqual(oto["bar"].offset, 100)
        self.assertEqual(oto["foo"].pre, 900)
        self.assertEqual(oto._datas_by_file["a"][0].alias, "bar")
        self.assertEqual(len(oto._datas_by_file["a"]), 1)
        self.assertEqual(oto["a\\foo"].pre, 900)
        self.assertFalse("a\\a" in oto._datas_by_file)

    @mock.patch("os.path.isdir")
    @mock.patch("os.listdir")
    @mock.patch("os.path.isfile")
    def test_load_nest_recursive(self, mock_isfile, mock_listdir, mock_isdir):
        mock_isfile.return_value = True
        mock_listdir.return_value = ["a", "oto.ini"]
        mock_isdir.side_effect = [True, True, False, False, False, False]
        lines = ["", "a", "b=1,2", "foo.wav=bar,100,600,200,900,-1000"]
        oto = voicebank.oto.Oto()
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io) as mocked_open:
            oto.load("voice", True)
        self.assertEqual(oto._datas_by_file[""][0].alias, "bar")
        self.assertEqual(len(oto._datas_by_file[""]), 1)
        self.assertEqual(oto["bar"].offset, 100)
        self.assertEqual(oto["foo"].pre, 900)
        self.assertEqual(oto._datas_by_file["a"][0].alias, "bar")
        self.assertEqual(len(oto._datas_by_file["a"]), 1)
        self.assertEqual(oto["a\\foo"].pre, 900)
        self.assertTrue("a\\a" in oto._datas_by_file)
        self.assertEqual(len(oto._datas_by_file["a\\a"]), 1)
        self.assertEqual(oto["a\\a\\foo"].pre, 900)

    @mock.patch("os.path.isdir")
    @mock.patch("os.listdir")
    @mock.patch("os.path.isfile")
    def test_load_nest_without_root_oto(self, mock_isfile, mock_listdir, mock_isdir):
        mock_isfile.return_value = True
        mock_isfile.side_effect = [False, mock.DEFAULT]
        mock_listdir.return_value = ["a", "oto.ini"]
        mock_isdir.side_effect = [True, False, False, False, False]
        lines = ["", "a", "b=1,2", "foo.wav=bar,100,600,200,900,-1000"]
        oto = voicebank.oto.Oto()
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io) as mocked_open:
            oto.load("voice")
        self.assertFalse("" in oto._datas_by_file)
        self.assertEqual(oto._datas_by_file["a"][0].alias, "bar")
        self.assertEqual(len(oto._datas_by_file["a"]), 1)
        self.assertEqual(oto["a\\foo"].pre, 900)
        self.assertEqual(oto["bar"].offset, 100)
        self.assertFalse("a\\a" in oto._datas_by_file)

    @mock.patch("os.path.isdir")
    @mock.patch("os.listdir")
    @mock.patch("os.path.isfile")
    def test_load_nest_recursive_without_root_oto(self, mock_isfile, mock_listdir, mock_isdir):
        mock_isfile.return_value = True
        mock_isfile.side_effect = [False, mock.DEFAULT, mock.DEFAULT]
        mock_listdir.return_value = ["a", "oto.ini"]
        mock_isdir.side_effect = [True, True, False, False, False, False]
        lines = ["", "a", "b=1,2", "foo.wav=bar,100,600,200,900,-1000"]
        oto = voicebank.oto.Oto()
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io) as mocked_open:
            oto.load("voice", True)
        self.assertFalse("" in oto._datas_by_file)
        self.assertEqual(oto._datas_by_file["a"][0].alias, "bar")
        self.assertEqual(len(oto._datas_by_file["a"]), 1)
        self.assertEqual(oto["a\\foo"].pre, 900)
        self.assertEqual(oto["bar"].offset, 100)
        self.assertTrue("a\\a" in oto._datas_by_file)
        self.assertEqual(len(oto._datas_by_file["a\\a"]), 1)
        self.assertEqual(oto["a\\a\\foo"].pre, 900)

    @mock.patch("os.listdir")
    @mock.patch("os.path.isfile")
    def test_init_with_load_single(self, mock_isfile, mock_listdir):
        mock_isfile.return_value = True
        mock_listdir.return_value = []
        lines = ["", "a", "b=1,2", "foo.wav=bar,100,600,200,900,-1000"]
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io) as mocked_open:
            oto = voicebank.oto.Oto("voice")
        self.assertEqual(oto._datas_by_file[""][0].alias, "bar")
        self.assertEqual(len(oto._datas_by_file[""]), 1)
        self.assertEqual(oto["bar"].offset, 100)
        self.assertEqual(oto["foo"].pre, 900)
