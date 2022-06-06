'''
voicebankモジュールのテスト
'''


import unittest
from unittest import mock

import os
import os.path
import logging

import voicebank
import settings.logger

class VoiceBankStaticTest(unittest.TestCase):
    '''
    staticmethodのテスト
    '''
    @mock.patch("os.listdir")
    @mock.patch("os.path.isdir")
    def test_is_utau_voicebank_in_charactertxt(self, mock_isdir, mock_listdir):
        '''dirpathが存在し、直下にcharacter.txtがある場合True
        '''
        mock_isdir.return_value = True
        mock_listdir.return_value = ["character.txt"]
        self.assertTrue(voicebank.VoiceBank.is_utau_voicebank("a"))

        
    @mock.patch("os.listdir")
    @mock.patch("os.path.isdir")
    def test_is_utau_voicebank_in_otoini(self, mock_isdir, mock_listdir):
        '''dirpathが存在し、直下にoto.iniがある場合True
        '''
        mock_isdir.return_value = True
        mock_listdir.return_value = ["oto.ini"]
        self.assertTrue(voicebank.VoiceBank.is_utau_voicebank("a"))
        
    @mock.patch("os.listdir")
    @mock.patch("os.path.isdir")
    def test_is_utau_voicebank_in_wav(self, mock_isdir, mock_listdir):
        '''dirpathが存在し、直下にwavファイルがある場合True
        '''
        mock_isdir.return_value = True
        mock_listdir.return_value = ["a.wav"]
        self.assertTrue(voicebank.VoiceBank.is_utau_voicebank("a"))
        mock_listdir.return_value = ["a.Wav"]
        self.assertTrue(voicebank.VoiceBank.is_utau_voicebank("a"))
        mock_listdir.return_value = ["a.WAV"]
        self.assertTrue(voicebank.VoiceBank.is_utau_voicebank("a"))
        mock_listdir.return_value = ["a.wav", "a_wav.frq"]
        self.assertTrue(voicebank.VoiceBank.is_utau_voicebank("a"))
        mock_listdir.return_value = ["a_wav.frq", "a.wav"]
        self.assertTrue(voicebank.VoiceBank.is_utau_voicebank("a"))

        
    @mock.patch("os.listdir")
    @mock.patch("os.path.isdir")
    def test_is_utau_voicebank_is_false(self, mock_isdir, mock_listdir):
        '''dirpathが存在し、直下にcharacter.txt,oto.ini,wavファイルのいずれもが存在しない場合
        '''
        mock_isdir.return_value = True
        mock_listdir.return_value = ["a_wav.frq"]
        self.assertFalse(voicebank.VoiceBank.is_utau_voicebank("a"))

        
    @mock.patch("os.listdir")
    @mock.patch("os.path.isdir")
    def test_is_utau_voicebank_is_not_found(self, mock_isdir, mock_listdir):
        '''dirpathがディレクトリでない場合、FileNotFoundErrorを返す
        '''
        mock_isdir.return_value = False
        mock_listdir.return_value = ["a.wav"]
        with self.assertRaises(FileNotFoundError) as cm:
            voicebank.VoiceBank.is_utau_voicebank("a")
        self.assertEqual(cm.exception.args[0], "{} is not found or not directory".format("a"))

class VoiceBankInitTest(unittest.TestCase):
    @mock.patch("voicebank.VoiceBank.is_utau_voicebank")
    def test_dirpath_is_not_utau(self, mock_is_utau):
        '''指定したフォルダがUTAU音源ではないとき
        '''
        mock_is_utau.return_value = False
        with self.assertRaises(ValueError) as cm:
            v = voicebank.VoiceBank("a")
        self.assertEqual(cm.exception.args[0], "{} is not utau voicebanks".format("a"))
        
    @mock.patch("os.listdir")
    @mock.patch("voicebank.VoiceBank.is_utau_voicebank")
    def test_loadfile_is_not_found(self, mock_is_utau, mock_listdir):
        '''指定したフォルダがUTAU音源で、character.txt,oto.ini,prefix.mapが見つからないとき
        '''
        test_logger = settings.logger.get_logger("TEST", True)

        mock_is_utau.return_value = True
        mock_listdir.return_value = []
        with self.assertLogs(logger=test_logger, level=logging.DEBUG) as cm:
            v = voicebank.VoiceBank("a", logger=test_logger)
        self.assertEqual(cm.output[0], ("WARNING:TEST:FileNotFoundError: a\character.txt is not found."))
        self.assertEqual(cm.output[1], ("INFO:TEST:oto.ini is loaded.files 0, records 0"))
        self.assertEqual(cm.output[2], ("WARNING:TEST:FileNotFoundError: a\prefix.map is not found."))
        
    @mock.patch("os.path.isfile")
    @mock.patch("os.listdir")
    @mock.patch("voicebank.VoiceBank.is_utau_voicebank")
    def test_loadfile_found_character_txt(self, mock_is_utau, mock_listdir, mock_isfile):
        '''指定したフォルダがUTAU音源で、character.txtのみ見つかったとき
        '''
        test_logger = settings.logger.get_logger("TEST", True)

        mock_is_utau.return_value = True
        mock_listdir.return_value = []
        mock_isfile.side_effect = [True, False, False]
        
        lines = ["name:名前",
                 "image:画像",
                 "sample:サンプル音声",
                 "author:管理者",
                 "web:https://sample.co.jp/",
                 "version:単独音1"]
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io):
            with self.assertLogs(logger=test_logger, level=logging.DEBUG) as cm:
                v = voicebank.VoiceBank("a", logger=test_logger)
        self.assertEqual(cm.output[0], ("INFO:TEST:character.txt is loaded. VBName:名前"))
        self.assertEqual(cm.output[1], ("INFO:TEST:oto.ini is loaded.files 0, records 0"))
        self.assertEqual(cm.output[2], ("WARNING:TEST:FileNotFoundError: a\prefix.map is not found."))
        
    @mock.patch("os.path.isfile")
    @mock.patch("os.listdir")
    @mock.patch("voicebank.VoiceBank.is_utau_voicebank")
    def test_loadfile_found_oto_ini(self, mock_is_utau, mock_listdir, mock_isfile):
        '''指定したフォルダがUTAU音源で、oto.iniのみ見つかったとき
        '''
        test_logger = settings.logger.get_logger("TEST", True)

        mock_is_utau.return_value = True
        mock_listdir.return_value = []
        mock_isfile.side_effect = [False, True, False]
        
        lines = ["", "a", "b=1,2", "foo.wav=bar,100,600,200,900,-1000"]
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io):
            with self.assertLogs(logger=test_logger, level=logging.DEBUG) as cm:
                v = voicebank.VoiceBank("a", logger=test_logger)
        self.assertEqual(cm.output[0], ("WARNING:TEST:FileNotFoundError: a\character.txt is not found."))
        self.assertEqual(cm.output[1], ("INFO:TEST:oto.ini is loaded.files 1, records 2"))
        self.assertEqual(cm.output[2], ("WARNING:TEST:FileNotFoundError: a\prefix.map is not found."))
        
    @mock.patch("os.path.isfile")
    @mock.patch("os.listdir")
    @mock.patch("voicebank.VoiceBank.is_utau_voicebank")
    def test_loadfile_found_prefix_map(self, mock_is_utau, mock_listdir, mock_isfile):
        '''指定したフォルダがUTAU音源で、prefix.mapのみ見つかったとき
        '''
        test_logger = settings.logger.get_logger("TEST", True)

        mock_is_utau.return_value = True
        mock_listdir.return_value = []
        mock_isfile.side_effect = [False, False, True]
        
        lines = ["", "a", "b=1,2", "foo.wav=bar,100,600,200,900,-1000"]
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io):
            with self.assertLogs(logger=test_logger, level=logging.DEBUG) as cm:
                v = voicebank.VoiceBank("a", logger=test_logger)
        self.assertEqual(cm.output[0], ("WARNING:TEST:FileNotFoundError: a\character.txt is not found."))
        self.assertEqual(cm.output[1], ("INFO:TEST:oto.ini is loaded.files 0, records 0"))
        self.assertEqual(cm.output[2], ("INFO:TEST:prefix.map is loaded"))
