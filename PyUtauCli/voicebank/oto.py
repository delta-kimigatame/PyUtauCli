import os.path
import wave


class OtoRecord:
    '''oto.iniの各行のデータを扱います。

    Attributes
    ----------
    otopath: str
        oto.iniのパス。voicedirからの相対パスで与えられる
    filename: str
        wavファイルのファイル名
    alias: str
        エイリアス
    offset: float
        オフセット(setparamでいうところの左ブランク)
    pre: float
        先行発声
    ove: float
        オーバーラップ
    consonant: float
        子音部(setparamでいうところの固定範囲)
    blank: float
        | ブランク(setparamでいうところの右ブランク)
        | 正の値のときはwav末尾からのmsを表す。
        | 負の値のときはオフセットからのmsの絶対値に-1をかけたものを表す。
    '''

    otopath: str
    filename: str
    alias: str
    offset: float
    pre: float
    ove: float
    consonant: float
    blank: float

    def __init__(self, otopath: str, filename: str, alias: str, offset: float, pre: float, ove: float, consonant: float, blank: float):
        '''oto.iniの各行のデータを扱います。

        Parameters
        ----------
        otopath: str
            oto.iniのパス。voicedirからの相対パスで与えられる
        filename: str
            wavファイルのファイル名
        alias: str
            エイリアス
        offset: float
            オフセット(setparamでいうところの左ブランク)
        pre: float
            先行発声
        ove: float
            オーバーラップ
        consonant: float
            子音部(setparamでいうところの固定範囲)
        blank: float
            | ブランク(setparamでいうところの右ブランク)
            | 正の値のときはwav末尾からのmsを表す。
            | 負の値のときはオフセットからのmsの絶対値に-1をかけたものを表す。
        '''
        self.otopath = otopath
        self.filename = filename
        self.alias = alias
        self.offset = offset
        self.pre = pre
        self.ove = ove
        self.consonant = consonant
        self.blank = blank

    def invert_blank(self, dirpath: str):
        '''
        | self.blank値の正負を反転します。
        | blankは正の数の時、ノート末尾からの長さms
        | 負の数の時、その絶対値がoffsetからの長さmsを表します。

        Parameters
        ----------
        dirpath: str
            音源のルートディレクトリのパス。

        Raises
        ------
        FileNotFoundError
            os.path.join(dirpath, self.otopath, self.filename)のwavファイルが見つからなかったとき
        wave.Error
            os.path.join(dirpath, self.otopath, self.filename)がwavファイルではなかったとき
        '''
        if os.path.isfile(os.path.join(dirpath, self.otopath, self.filename)):
            raise FileNotFoundError("{} is not found.".format(filepath))
        with wave.open(os.path.join(dirpath, self.otopath, self.filename), "rb") as wr:
            wav_length = wr.getnframes() / wr.getframerate() * 1000
        if self.blank >= 0:
            self.blank = self.offset - (wav_length - self.blank)
        else:
            self.blank = wav_length - (self.offset - self.blank)
