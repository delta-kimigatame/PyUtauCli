'''
windows版UTAUの情報を取得します。
'''


import platform
import winreg
import os
import os.path


def is_utau_installed() -> bool:
    '''
    UTAUがインストールされているか確認します。

    Returns
    -------
    is_utau_installed: bool

        | レジストリのHKEY_CLASSES_ROOT\\\\UTAUSequenceTextが存在すれば、インストール済みとみなしTrueを返します。
        | windows以外の環境ではFalseを返します。
    '''
    if not platform.platform().startswith("Windows"):
        return False

    subkeys: list = []
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "") as key:
        subKeyNum: int = winreg.QueryInfoKey(key)[0]
        for i in range(subKeyNum):
            subkeys.append(winreg.EnumKey(key, i))

    return "UTAUSequenceText" in subkeys


def get_utau_root() -> str:
    '''
    UTAU.exeの場所を返します。

    Returns
    -------
    dir_name: str

        | UTAU.exeの場所
        | レジストリのHKEY_CLASSES_ROOT\\\\UTAUSequenceText\\\\shell\\\\open\\\\commandから取得します。
        | UTAUがインストールされていない場合、""を返します。
        | windows以外の環境では""を返します。

    '''

    if not platform.platform().startswith("Windows"):
        return ""
    if not is_utau_installed():
        return ""
    reg_value: str
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "UTAUSequenceText\\shell\\open\\command") as key:
        reg_value = winreg.EnumValue(key, 0)
    return os.path.dirname(" ".join(reg_value[1].split(" ")[:-1]).replace("\"", ""))


def get_utau_settings(utau_root: str="") -> dict:
    '''
    | UTAUのsetting.iniを読み込みます。
    | 読み込む優先順位は下記のとおりです。

    1. (UTAUが program files(x86)にインストールされている場合) %LOCALAPPDATA%\\\\VirtualStore\\\\program files(x86)\\\\UTAU\\\\setting.ini
    2. (ほかのフォルダにインストールされているか、上記のフォルダになければ) {UTAU_ROOT}\\\\setting.ini

    Parameters
    ----------
    utau_root: str, default ""
        UTAUのパス
        初期値の場合、*get_utau_root* を呼び出します。

    Returns
    -------
    utau_settings: dict
        UTAUのsetting.iniの内容を読み込んだ辞書ファイル
        見つからなければ空の辞書を返します。

    '''
    if utau_root == "":
        utau_root = get_utau_root()

    if utau_root == "":
        return {}

    settings_path: str = os.path.join(utau_root, "setting.ini")
    read_datas: list
    utau_settings: dict = {}
    if "program files(x86)" in utau_root:
        path_tail: str = utau_root.split("program files(x86)")[1].replace("\\", "")
        if os.path.isfile(os.path.join(os.environ["localappdata"], "VirtualStore", "program files(x86)", path_tail, "setting.ini")):
            settings_path = os.path.join(os.environ["localappdata"], "VirtualStore", "program files(x86)", path_tail, "setting.ini")

    with open(settings_path, "r") as fr:
        read_datas = fr.read().replace("\r", "").split("\n")

    for data in read_datas:
        if "=" not in data:
            continue
        tmp = data.split("=")
        utau_settings[tmp[0]] = tmp[1]

    return utau_settings
