'''
voicebank.characterモジュールのテスト
'''


import unittest
from unittest import mock

import os
import os.path

import voicebank.character

class CharacterReadTest(unittest.TestCase):
    '''
    character.txt読み込みに関するテスト
    '''
    def test_init(self):
        '''
        初期化に関するテスト
        '''
        character = voicebank.character.Character()
        self.assertEqual(character.name, "")
        self.assertEqual(character.image, "")
        self.assertEqual(character.sample, "")
        self.assertEqual(character.author, "")
        self.assertEqual(character.web, "")
        self.assertEqual(character.version, "")

    @mock.patch("os.path.isfile")
    def test_load_equal(self, mock_isfile):
        '''
        "="区切りのcharacter.txtを読み込んだ際のテスト
        '''
        mock_isfile.return_value = True
        lines=["name=名前",
               "image=画像",
               "sample=サンプル音声",
               "author=管理者",
               "web=https://sample.co.jp/",
               "version=単独音1"]
        character = voicebank.character.Character()
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io):
            character.load("samplepath")
        self.assertEqual(character.name, "名前")
        self.assertEqual(character.image, "画像")
        self.assertEqual(character.sample, "サンプル音声")
        self.assertEqual(character.author, "管理者")
        self.assertEqual(character.web, "https://sample.co.jp/")
        self.assertEqual(character.version, "単独音1")
        
    @mock.patch("os.path.isfile")
    def test_load_colon(self, mock_isfile):
        '''
        ":"区切りのcharacter.txtを読み込んだ際のテスト
        '''
        mock_isfile.return_value = True
        lines=["name:名前",
               "image:画像",
               "sample:サンプル音声",
               "author:管理者",
               "web:https://sample.co.jp/",
               "version:単独音1"]
        character = voicebank.character.Character()
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io):
            character.load("samplepath")
        self.assertEqual(character.name, "名前")
        self.assertEqual(character.image, "画像")
        self.assertEqual(character.sample, "サンプル音声")
        self.assertEqual(character.author, "管理者")
        self.assertEqual(character.web, "https://sample.co.jp/")
        self.assertEqual(character.version, "単独音1")
        
    @mock.patch("os.path.isfile")
    def test_load_mixture(self, mock_isfile):
        '''
        区切り文字が混在したのcharacter.txtを読み込んだ際のテスト
        '''
        mock_isfile.return_value = True
        lines=["name=名前",
               "image:画像",
               "sample:サンプル音声",
               "author=管理者",
               "web:https://sample.co.jp/",
               "version:単独音1"]
        character = voicebank.character.Character()
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io):
            character.load("samplepath")
        self.assertEqual(character.name, "名前")
        self.assertEqual(character.image, "画像")
        self.assertEqual(character.sample, "サンプル音声")
        self.assertEqual(character.author, "管理者")
        self.assertEqual(character.web, "https://sample.co.jp/")
        self.assertEqual(character.version, "単独音1")
        
    @mock.patch("os.path.isfile")
    def test_load_no_value(self, mock_isfile):
        '''
        | 空のcharacter.txtを読み込んだ際のテスト
        | 名前が存在しないとき、フォルダ名の末尾になる。
        '''
        mock_isfile.return_value = True
        lines=[""]
        character = voicebank.character.Character()
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io):
            character.load(os.path.join("voice","sample1"))
        self.assertEqual(character.name, "sample1")
        self.assertEqual(character.image, "")
        self.assertEqual(character.sample, "")
        self.assertEqual(character.author, "")
        self.assertEqual(character.web, "")
        self.assertEqual(character.version, "")
        
    @mock.patch("os.path.isfile")
    def test_load_raise_not_found(self, mock_isfile):
        '''
        | character.txtが存在しなかったときのテスト
        '''
        mock_isfile.return_value = False
        lines=[""]
        character = voicebank.character.Character()
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        
        with self.assertRaises(FileNotFoundError) as cm:
            character.load(os.path.join("voice","sample1"))
        self.assertEqual(cm.exception.args[0],"{} is not found.".format(os.path.join("voice","sample1","character.txt")))
        
    @mock.patch("os.path.isfile")
    def test_load_raise_unicode_decode_error(self, mock_isfile):
        '''
        | character.txtシステムデフォルトでもcp932でも開けなかったとき
        '''
        mock_isfile.return_value = True
        lines=[""]
        character = voicebank.character.Character()
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        
        with self.assertRaises(UnicodeDecodeError) as cm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                mocked_open.side_effect=UnicodeDecodeError("cp932",b"\x00\x00",1,2,"reason")
                character.load(os.path.join("voice","sample1"))
        self.assertEqual(cm.exception.reason,"can't read character.txt. because required character encoding is system default or cp932")
        
    @mock.patch("os.path.isfile")
    def test_load_raise_unicode_decode_error_once(self, mock_isfile):
        '''
        | character.txtシステムデフォルトで開けなかったがcp932で開けたとき
        '''
        mock_isfile.return_value = True
        lines=["name=名前",
               "image=画像",
               "sample=サンプル音声",
               "author=管理者",
               "web=https://sample.co.jp/",
               "version=単独音1"]
        character = voicebank.character.Character()
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        
        with mock.patch("builtins.open", mock_io) as mocked_open:
            mocked_open.side_effect=[UnicodeDecodeError("cp932",b"\x00\x00",1,2,"reason"), mock.DEFAULT]
            character.load(os.path.join("voice","sample1"))
        self.assertEqual(character.name, "名前")
        self.assertEqual(character.image, "画像")
        self.assertEqual(character.sample, "サンプル音声")
        self.assertEqual(character.author, "管理者")
        self.assertEqual(character.web, "https://sample.co.jp/")
        self.assertEqual(character.version, "単独音1")
        
    @mock.patch("os.path.isfile")
    def test_load_init_with_load(self, mock_isfile):
        '''
        "="区切りのcharacter.txtを読み込んだ際のテスト
        '''
        mock_isfile.return_value = True
        lines=["name=名前",
               "image=画像",
               "sample=サンプル音声",
               "author=管理者",
               "web=https://sample.co.jp/",
               "version=単独音1"]
        mock_io = mock.mock_open(read_data="\r\n".join(lines))
        with mock.patch("builtins.open", mock_io):
            character = voicebank.character.Character("samplepath")
        self.assertEqual(character.name, "名前")
        self.assertEqual(character.image, "画像")
        self.assertEqual(character.sample, "サンプル音声")
        self.assertEqual(character.author, "管理者")
        self.assertEqual(character.web, "https://sample.co.jp/")
        self.assertEqual(character.version, "単独音1")