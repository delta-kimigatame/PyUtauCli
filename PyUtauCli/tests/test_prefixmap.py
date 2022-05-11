'''
voicebank.prefixmapモジュールのテスト
'''


import unittest
from unittest import mock

import os
import os.path

import voicebank.prefixmap


class MapRecordTest(unittest.TestCase):
    '''
    PrefixMapの各行の値に関するテスト
    '''

    def test_init(self):
        '''
        正常に初期化できる場合のテスト
        '''
        record = voicebank.prefixmap.MapRecord("C4\tpre\tsu")
        self.assertEqual(record.key, "C4")
        self.assertEqual(record.prefix, "pre")
        self.assertEqual(record.suffix, "su")

    def test_init_bad_format(self):
        '''
        不正な値で初期化しようとした際のテスト
        '''
        with self.assertRaises(ValueError) as cm:
            record = voicebank.prefixmap.MapRecord("C4\tpre")
        self.assertEqual(cm.exception.args[0], "can't set prefix map value.C4\tpre is bad format.")


class PrefixMapTest(unittest.TestCase):
    '''
    prefix.mapの読み書きに関するテスト
    '''

    def test_default_init(self):
        '''
        | 引数無しでprefix.mapを初期化する場合。
        | 同一のrecordに音高番号と音高名どちらでもアクセスできることを確認する。
        '''
        prefix = voicebank.prefixmap.PrefixMap()
        self.assertEqual(len(prefix._key), 108 - 24)
        self.assertEqual(prefix._key[0], 24)
        self.assertEqual(prefix._key[-1], 107)
        self.assertEqual(prefix[24], prefix["C1"])
        self.assertNotEqual(prefix[24], prefix["C#1"])
        self.assertEqual(prefix[25], prefix["C#1"])
        self.assertEqual(prefix[25], prefix["C♯1"])
        self.assertEqual(prefix[25], prefix["Db1"])
        self.assertEqual(prefix[25], prefix["D♭1"])
        self.assertEqual(prefix[107], prefix["B7"])

    @mock.patch("os.path.isfile")
    def test_load_raise_file_not_found_error(self, mock_isfile):
        '''
        prefix.mapが存在しなかったときのテスト
        '''
        mock_isfile.return_value = False
        with self.assertRaises(FileNotFoundError) as cm:
            prefix = voicebank.prefixmap.PrefixMap(os.path.join("voice", "sample"))
        self.assertEqual(cm.exception.args[0], "{} is not found.".format(os.path.join("voice", "sample", "prefix.map")))

    @mock.patch("os.path.isfile")
    def test_load_raise_file_not_found_error_with_set_path(self, mock_isfile):
        '''
        標準以外のファイル名を指定したとき
        '''
        mock_isfile.return_value = False
        prefix = voicebank.prefixmap.PrefixMap()
        with self.assertRaises(FileNotFoundError) as cm:
            prefix = prefix.load(os.path.join("voice", "sample"), "test.map")
        self.assertEqual(cm.exception.args[0], "{} is not found.".format(os.path.join("voice", "sample", "test.map")))

    @mock.patch("os.path.isfile")
    def test_load_raise_unicode_decode_error(self, mock_isfile):
        '''
        prefix.mapがutf-8でもcp932でも開けなかったとき
        '''
        mock_isfile.return_value = True
        lines = [""]
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with self.assertRaises(UnicodeDecodeError) as cm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                mocked_open.side_effect = UnicodeDecodeError("cp932", b"\x00\x00", 1, 2, "reason")
                prefix = voicebank.prefixmap.PrefixMap(os.path.join("voice", "sample"))
        self.assertEqual(cm.exception.reason, "can't read prefix.map. because required character encoding is utf-8 or cp932")

    @mock.patch("os.path.isfile")
    def test_load(self, mock_isfile):
        '''
        prefix.mapが開けたとき
        '''
        mock_isfile.return_value = True
        lines = ["C1\t_preC1\t_suC1",
                 "",
                 "a",
                 "C4\t_preC4\t_suC4"]
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io) as mocked_open:
            prefix = voicebank.prefixmap.PrefixMap(os.path.join("voice", "sample"))
        self.assertEqual(prefix["C1"].prefix, "_preC1")
        self.assertEqual(prefix["C1"].suffix, "_suC1")
        self.assertEqual(prefix["C4"].prefix, "_preC4")
        self.assertEqual(prefix["C4"].suffix, "_suC4")

    @mock.patch("os.path.isfile")
    def test_load_raise_unicode_decode_error_once(self, mock_isfile):
        '''
        prefix.mapがcp932で開けなかったがutf-8で開けたとき
        '''
        mock_isfile.return_value = True
        lines = ["C1\t_preC1\t_suC1",
                 "",
                 "a",
                 "C4\t_preC4\t_suC4"]
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io) as mocked_open:
            mocked_open.side_effect = [UnicodeDecodeError("cp932", b"\x00\x00", 1, 2, "reason"), mock.DEFAULT]
            prefix = voicebank.prefixmap.PrefixMap(os.path.join("voice", "sample"))
        self.assertEqual(prefix["C1"].prefix, "_preC1")
        self.assertEqual(prefix["C1"].suffix, "_suC1")
        self.assertEqual(prefix["C4"].prefix, "_preC4")
        self.assertEqual(prefix["C4"].suffix, "_suC4")

    @mock.patch("os.path.isfile")
    def test_save(self, mock_isfile):
        '''
        | prefix.mapの保存を確認する。
        | 値がない項目はprefixとsuffixが空欄で保存されることを確認する。
        '''
        mock_isfile.return_value = True
        lines = ["C1\t_preC1\t_suC1",
                 "",
                 "a",
                 "C4\t_preC4\t_suC4"]
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io) as mocked_open:
            prefix = voicebank.prefixmap.PrefixMap(os.path.join("voice", "sample"))
            prefix.save(os.path.join("voice", "sample"))

        self.assertEqual(len(mock_io().write.call_args_list), 108 - 24)
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "B7\t\t\r\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "A#7\t\t\r\n")
        self.assertEqual(mock_io().write.call_args_list[-1][0][0], "C1\t_preC1\t_suC1\r\n")
