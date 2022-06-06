'''
voicebankモジュールのテスト
'''


import unittest
from unittest import mock

import os
import os.path

import voicebank

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
            self.assertFalse(voicebank.VoiceBank.is_utau_voicebank("a"))
        self.assertEqual(cm.exception.args[0], "{} is not found or not directory".format("a"))