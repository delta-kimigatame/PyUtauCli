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
