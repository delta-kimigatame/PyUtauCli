'''
settingsモジュールのうち、環境に応じて自動で値が代入されるもののテスト
'''


import unittest
from unittest import mock

import os
import os.path

import settings


class WinUtauSettingsTest(unittest.TestCase):
    '''
    windowsの環境変数やUTAUの導入状況に応じて値の替わるsettingsのテスト
    '''
    @mock.patch("platform.platform")
    def test_is_utau_installed_not_windows(self, mock_platform):
        '''settings.win_utau.is_utau_installedは非windows環境でFalse
        '''
        mock_platform.return_value = "Linux-5.4.144+-x86_64-with-Ubuntu-18.04-bionic"
        self.assertFalse(settings.win_utau.is_utau_installed())
        
    @mock.patch("winreg.EnumKey")
    @mock.patch("winreg.QueryInfoKey")
    @mock.patch("platform.platform")
    def test_is_utau_installed_windows_no_installed(self, mock_platform, mock_QueryInfoKey, mock_enumkey):
        '''settings.win_utau.is_utau_installedはwindows環境ではHKEY_CLASSES_ROOT\\\\UTAUSequenceTextが存在しなければFalse
        '''
        mock_platform.return_value = "Windows-10-10.0.22000-SP0"
        mock_QueryInfoKey.return_value = [1, 1, 1]
        mock_enumkey.return_value = ""
        self.assertFalse(settings.win_utau.is_utau_installed())
        
    @mock.patch("winreg.EnumKey")
    @mock.patch("winreg.QueryInfoKey")
    @mock.patch("platform.platform")
    def test_is_utau_installed_windows_installed(self, mock_platform, mock_QueryInfoKey, mock_enumkey):
        '''settings.win_utau.is_utau_installedはwindows環境ではHKEY_CLASSES_ROOT\\\\UTAUSequenceTextが存在すればTrue
        '''
        mock_platform.return_value = "Windows-10-10.0.22000-SP0"
        mock_QueryInfoKey.return_value = [1, 1, 1]
        mock_enumkey.return_value = "UTAUSequenceText"
        self.assertTrue(settings.win_utau.is_utau_installed())
        
    @mock.patch("platform.platform")
    def test_get_utau_root_not_windows(self, mock_platform):
        '''settings.win_utau.get_utau_rootは非windows環境で""
        '''
        mock_platform.return_value = "Linux-5.4.144+-x86_64-with-Ubuntu-18.04-bionic"
        self.assertEqual(settings.win_utau.get_utau_root(), "")
        
    @mock.patch("settings.win_utau.is_utau_installed")
    @mock.patch("platform.platform")
    def test_get_utau_root_not_installed(self, mock_platform, mock_isInstalled):
        '''settings.win_utau.get_utau_rootはwindows環境でUTAUがインストールされていなければ""
        '''
        mock_platform.return_value = "Windows-10-10.0.22000-SP0"
        mock_isInstalled.return_value = False
        self.assertEqual(settings.win_utau.get_utau_root(), "")
        
    @mock.patch("winreg.EnumValue")
    @mock.patch("settings.win_utau.is_utau_installed")
    @mock.patch("platform.platform")
    def test_get_utau_root_installed_programfiles(self, mock_platform, mock_isInstalled, mock_enumkey):
        '''settings.win_utau.get_utau_rootはwindows環境でUTAUがインストールされていればそのルートフォルダ
        '''
        mock_platform.return_value = "Windows-10-10.0.22000-SP0"
        mock_isInstalled.return_value = True
        mock_enumkey.return_value = (0, '"C:\\program files(x86)\\UTAU\\utau.exe %1"', 1)
        self.assertEqual(settings.win_utau.get_utau_root(), 'C:\\program files(x86)\\UTAU')
        
    @mock.patch("winreg.EnumValue")
    @mock.patch("settings.win_utau.is_utau_installed")
    @mock.patch("platform.platform")
    def test_get_utau_root_installed_other_programfiles(self, mock_platform, mock_isInstalled, mock_enumkey):
        '''settings.win_utau.get_utau_rootはwindows環境でUTAUがインストールされていればそのルートフォルダ
        '''
        mock_platform.return_value = "Windows-10-10.0.22000-SP0"
        mock_isInstalled.return_value = True
        mock_enumkey.return_value = (0, '"C:\\UTAU\\utau.exe %1"', 1)
        self.assertEqual(settings.win_utau.get_utau_root(), 'C:\\UTAU')

    @mock.patch("settings.win_utau.get_utau_root")
    def test_get_utau_settings_not_path(self, mock_utauroot):
        '''settings.win_utau.get_utau_settingsは引数がなく、UTAUのパスが見つからなければ{}
        '''
        mock_utauroot.return_value = ""
        self.assertEqual(settings.win_utau.get_utau_settings(), {})
        
    @mock.patch("settings.win_utau.get_utau_root")
    def test_get_utau_settings_not_program_files(self, mock_utauroot):
        '''settings.win_utau.get_utau_settingsは引数がなく、UTAUのパスが見つかれば同じフォルダのsettings.iniを読み込む
        '''
        mock_utauroot.return_value = "C:\\UTAU"
        mock_io = mock.mock_open(read_data="text1=value1\r\ntext2=value2\r\ntext3=value3\r\n\r\n")
        with mock.patch("builtins.open", mock_io):
            result = settings.win_utau.get_utau_settings()
            mock_io.assert_called_once_with("C:\\UTAU\\setting.ini", "r")
        self.assertEqual(result, {"text1": "value1", "text2": "value2", "text3": "value3"})
        
    @mock.patch("os.path.isfile")
    @mock.patch("settings.win_utau.get_utau_root")
    def test_get_utau_settings_program_files_with_virtualstore(self, mock_utauroot, mock_isfile):
        '''
        | settings.win_utau.get_utau_settingsは引数がなく、UTAUのパスがprogram files(x86)にある場合、
        | %localappdata%\\\\VirtualStore\\\\program files(x86)のsettings.iniを読み込む
        '''
        mock_utauroot.return_value = "C:\\program files(x86)\\UTAU4"
        mock_isfile.return_value = True
        os.environ["localappdata"] = os.path.join("C:\\Users", "username", "Appdata", "Local")
        mock_io = mock.mock_open(read_data="text1=value1\r\ntext2=value2\r\ntext3=value3\r\n\r\n")
        with mock.patch("builtins.open", mock_io):
            result = settings.win_utau.get_utau_settings()
            mock_io.assert_called_once_with(os.path.join(os.environ["localappdata"], "VirtualStore", "program files(x86)", "UTAU4", "setting.ini"), "r")
        self.assertEqual(result, {"text1": "value1", "text2": "value2", "text3": "value3"})
        
    @mock.patch("os.path.isfile")
    @mock.patch("settings.win_utau.get_utau_root")
    def test_get_utau_settings_program_files(self, mock_utauroot, mock_isfile):
        '''
        | settings.win_utau.get_utau_settingsは引数がなく、UTAUのパスがprogram files(x86)にある場合かつ、
        | %localappdata%\\\\VirtualStore\\\\program files(x86)のsettings.iniがなければ、UTAUROOTのsetting.iniを読み込む
        '''
        mock_utauroot.return_value = "C:\\program files(x86)\\UTAU4"
        mock_isfile.return_value = False
        os.environ["localappdata"] = os.path.join("C:\\Users", "username", "Appdata", "Local")
        mock_io = mock.mock_open(read_data="text1=value1\r\ntext2=value2\r\ntext3=value3\r\n\r\n")
        with mock.patch("builtins.open", mock_io):
            result = settings.win_utau.get_utau_settings()
            mock_io.assert_called_once_with(os.path.join("C:\\program files(x86)", "UTAU4", "setting.ini"), "r")
        self.assertEqual(result, {"text1": "value1", "text2": "value2", "text3": "value3"})
        
    @mock.patch("os.path.isfile")
    @mock.patch("settings.win_utau.get_utau_root")
    def test_get_utau_settings_with_args(self, mock_utauroot, mock_isfile):
        '''
        | settings.win_utau.get_utau_settingsは引数があれば引数のフォルダにあるsetting.iniを読み込む
        '''
        mock_utauroot.return_value = "C:\\program files(x86)\\UTAU4"
        mock_isfile.return_value = False
        os.environ["localappdata"] = os.path.join("C:\\Users", "username", "Appdata", "Local")
        mock_io = mock.mock_open(read_data="text1=value1\r\ntext2=value2\r\ntext3=value3\r\n\r\n")
        with mock.patch("builtins.open", mock_io):
            result = settings.win_utau.get_utau_settings("C:\\UTAU")
            mock_io.assert_called_once_with(os.path.join("C:\\UTAU", "setting.ini"), "r")
        self.assertEqual(result, {"text1": "value1", "text2": "value2", "text3": "value3"})
