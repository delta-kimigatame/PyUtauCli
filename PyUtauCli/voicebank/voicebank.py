import os
import os.path
import traceback
from logging import Logger

import settings.logger
from .character import Character
from .prefixmap import PrefixMap
from .oto import Oto


default_logger = settings.logger.get_logger(__name__, False)


class VoiceBank:
    '''VoiceBank
    UTAUの音源データを扱います。
    
    Attributes
    ----------
    dirpath: str
        音源のルートパス

    character: Character
        character.txt

    oto: Oto
        oto.ini

    prefix: PrefixMap
        prefix.map
    '''

    _dirpath: str
    _character: Character
    _oto: Oto
    _prefix: PrefixMap

    @property
    def dirpath(self) -> str:
        return self._dirpath

    @property
    def character(self) -> Character:
        return self._character

    @property
    def oto(self) -> Oto:
        return self._oto

    @property
    def prefix(self) -> PrefixMap:
        return self._prefix

    def __init__(self, dirpath: str, *, logger:Logger = None):
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
        self.logger = logger or default_logger
        if not VoiceBank.is_utau_voicebank(dirpath):
            self.logger.error("{} is not utau voicebanks".format(dirpath))
            raise ValueError("{} is not utau voicebanks".format(dirpath))
        self._dirpath = dirpath
        try:
            self._character = Character(dirpath)
            self.logger.info("character.txt is loaded. VBName:{}".format(self._character.name))
        except Exception as e:
            self.logger.warn(traceback.format_exception_only(type(e), e)[0].rstrip('\n'))
            self._character = Character()
            
        try:
            self._oto = Oto(dirpath)
            self.logger.info("oto.ini is loaded.files {}, records {}".format(self._oto.files(), self._oto.records()))
        except Exception as e:
            self.logger.warn(traceback.format_exception_only(type(e), e)[0].rstrip('\n'))

        try:
            self._prefix = PrefixMap(dirpath)
            self.logger.info("prefix.map is loaded")
        except Exception as e:
            self.logger.warn(traceback.format_exception_only(type(e), e)[0].rstrip('\n'))
            self._prefix = PrefixMap()

    @staticmethod
    def is_utau_voicebank(dirpath: str, *, logger:Logger = None) -> bool:
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
        logger = logger or default_logger
        if not os.path.isdir(dirpath):
            logger.error("{} is not found or not directory".format(dirpath))
            raise FileNotFoundError("{} is not found or not directory".format(dirpath))
        logger.info("{} is found. checking directory".format(dirpath))
        files: list = os.listdir(dirpath)
        if "character.txt" in files:
            logger.info("{} is found.".format("character.txt"))
            return True
        elif "oto.ini" in files:
            logger.info("{} is found.".format("oto.ini"))
            return True
        elif ".wav:" in ":".join(files).lower():
            logger.info("{} is found.".format("wav file"))
            return True
        elif ":".join(files).lower().endswith(".wav"):
            logger.info("{} is found.".format("wav file"))
            return True
        else:
            return False

