'''Settins
各種定数や初期値の設定

Attributes
----------
UTAU_IS_INSTALLED: bool

    | UTAUがインストール済みか否か
    | windows以外の環境では自動的にFalseになる。

UTAU_ROOT: str, default ""

    | UTAUがインストールされたフォルダのパス

UTAU_SETTINGS: dict, default {}

    | UTAUのsetting.iniの内容を読み込んだ辞書ファイル

VOICE_ROOT: list of str

    | 音源フォルダのルート
    | windows環境では、UTAU.exeと同じ階層のsetting.iniに記載あり

'''

import platform
import os
import os.path

from . import win_utau

UTAU_IS_INSTALLED: bool = win_utau.is_utau_installed()
UTAU_SETTINGS: dict = {}
VOICE_ROOT: list = []
if UTAU_IS_INSTALLED:
    UTAU_ROOT: str = win_utau.get_utau_root()
    UTAU_SETTINGS = win_utau.get_utau_settings()
    if "VoiceRoot" in UTAU_SETTINGS:
        VOICE_ROOT.append(UTAU_SETTINGS["VoiceRoot"])
    VOICE_ROOT.append(os.path.join(os.environ["appdata"],"UTAU","voice"))
    VOICE_ROOT.append(os.path.join(UTAU_ROOT,"voice"))
else:
    UTAU_ROOT: str = ""



