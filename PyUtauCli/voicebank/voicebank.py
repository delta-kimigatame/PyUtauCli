import os
import os.path

from .character import Character


class VoiceBank:
    '''VoiceBank
    UTAUの音源データを扱います。
    
    Attributes
    ----------
    dirpath: str
        音源のルートパス

    character: Character
        character.txt
    '''

    _dirpath: str
    _character: Character

    @property
    def dirpath(self) -> str:
        return self._dirpath

    @property
    def character(self) -> Character:
        return self._character

    def __init__(self, dirpath: str):
        '''
        Parameters
        ----------
        dirpath: str
            音源のルートパス

        Raises
        ------
        FileNotFoundErrod
            指定したフォルダが見つからなかったとき

        ValueError
            指定したフォルダが音源フォルダではなかったとき
        '''
        if not VoiceBank.is_utau_voicebank(dirpath):
            raise ValueError("{} is not utau voicebanks".format(dirpath))

    @staticmethod
    def is_utau_voicebank(dirpath: str) -> bool:
        '''
        | 渡されたパスがUTAU音源フォルダか判定する。
        | character.txt、oto.ini、.wavのいずれかがあればUTAU音源フォルダと判定する。

        Parameters
        ----------
        dirpath: str
            音源のルートパス

        Returns
        -------
        is_utau_voicebank: bool
            
        Raises
        ------
        FileNotFoundErrod
            指定したフォルダが見つからなかったとき

        '''
        if not os.path.isdir(dirpath):
            raise FileNotFoundError("{} is not found or not directory".format(dirpath))
        files: list = os.listdir(dirpath)
        if "character.txt" in files:
            return True
        elif "oto.ini" in files:
            return True
        elif".wav:" in ":".join(files).lower():
            return True
        else:
            return False
