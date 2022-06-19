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
            | エイリアス
            | 空の値が与えられた場合、os.path.join(otopath, filename)から拡張子を除いたもので初期化する。
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
        if alias != "":
            self.alias = alias
        else:
            self.alias = ".".join(os.path.join(otopath, filename).split(".")[:-1])
        self.offset = float(offset)
        self.pre = float(pre)
        self.ove = float(ove)
        self.consonant = float(consonant)
        self.blank = float(blank)

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
        if not os.path.isfile(os.path.join(dirpath, self.otopath, self.filename)):
            raise FileNotFoundError("{} is not found.".format(os.path.join(dirpath, self.otopath, self.filename)))
        with wave.open(os.path.join(dirpath, self.otopath, self.filename), "rb") as wr:
            wav_length = wr.getnframes() / wr.getframerate() * 1000
        if self.blank >= 0:
            self.blank = self.offset - (wav_length - self.blank)
        else:
            self.blank = wav_length - (self.offset - self.blank)


class Oto:
    '''oto.iniのデータを扱います。
    '''
    _values: dict = {}
    _datas_by_file: dict = {}

    def __init__(self, dirpath: str = ""):
        '''
        Parameters
        ----------
        dirpath: str, default ""
            音源のルートディレクトリのパス。引数が与えられている場合self.load(dirpath)を実行する。

        Raises
        ------
        FileNotFoundError
            load実行時oto.iniが見つからなかった場合
        UnicodeDecodeError
            load実行時ファイルがcp932でもutf-8でもなかった場合
        '''

        self._values = {}
        self._datas_by_file = {}
        if dirpath != "":
            self.load(dirpath)

    def files(self) -> int:
        '''
        読み込んだoto.iniファイルの数を返す

        Return
        ------
        len(self._datas_by_file): int
        '''
        return len(self._datas_by_file)

    def records(self) -> int:
        '''
        読み込んだoto.iniの合計行数を返す

        Return
        ------
        len(self._values): int
        '''
        return len(self._values)

    def __getitem__(self, key) -> OtoRecord:
        return self._values[key]

    def haskey(self, key) -> bool:
        return key in self._values

    def load(self, dirpath: str, recursive: bool = False, subdir: str = ""):
        '''
        | dirpathおよびその子フォルダのoto.iniを読み込みself._datas_by_fileとself._valuesを更新する。
        | self._datas_by_fileはdirpathからの相対パスをキーに持つ辞書で、OtoRecord形式のlistを格納する。
        | self._valuesはaliasをkeyとする辞書で、self._datas_by_fileを参照する。
        | aliasの衝突が起きた場合、ファイル名が若いものを参照する。
        | 同一ファイル内でaliasの衝突が起きた場合、offset値の小さいものを参照する。


        Parameters
        ----------
        dirpath: str
            音源のルートディレクトリのパス

        recursive: bool, default False
            | Trueにすると孫フォルダ以下のoto.iniも探索する。

        subdir: str, default ""
            音源ルートディレクトリからの相対パス

        Raises
        ------
        UnicodeDecodeError
            ファイルがcp932でもutf-8でもなかった場合

        '''

        if os.path.isfile(os.path.join(dirpath, subdir, "oto.ini")):
            self._loadFile(os.path.join(dirpath, subdir, "oto.ini"), subdir)
        if subdir == "" or recursive:
            for filename in os.listdir(os.path.join(dirpath, subdir)):
                if os.path.isdir(os.path.join(dirpath, subdir, filename)):
                    self.load(dirpath, recursive, os.path.join(subdir, filename))
                    
    def _setValue(self, alias: str, record: OtoRecord):
        '''
        | self._values[alias]に値をセットする。
        | self._values[alias]が既に存在する場合、ファイル名が若いものをセットする。
        | ファイル名も同じの場合、offsetが小さいものをセットする。

        Parameters
        ----------
        alias: str
            self._valuesのkeyとなるalias

        record: OtoRecord
        '''
        
        if alias not in self._values:
            self._values[alias]=record
        elif record.filename == self._values[alias].filename and record.offset < self._values[alias].offset:
            self._values[alias]=record
        elif record.filename < self._values[alias].filename:
            self._values[alias]=record

    def _loadFile(self, otopath: str, subdir: str):
        '''
        | otopathのoto.iniを読み込みself._datas_by_fileとself._valuesを更新する。
        | ファイルの存在は事前に確認されていること
        
        Parameters
        ----------
        otopath: str
            音源のルートディレクトリのパス

        subdir: str, default ""
            音源ルートディレクトリからの相対パス

        Raises
        ------
        UnicodeDecodeError
            ファイルがcp932でもutf-8でもなかった場合
        '''
        try:
            with open(otopath, "r", encoding="cp932") as fr:
                lines=fr.read().replace("\r", "").split("\n")
        except:
            try:
                with open(otopath, "r", encoding="utf-8") as fr:
                    lines=fr.read().replace("\r", "").split("\n")
            except UnicodeDecodeError as e:
                e.reason="can't read {}. because required character encoding is utf-8 or cp932".format(otopath)
                raise e
        self._datas_by_file[subdir]=[]
        for line in lines:
            if line == "":
                continue
            if "=" not in line:
                continue
            if "," not in line:
                continue
            filename, param=line.split("=")
            params=param.split(",")
            if len(params) != 6:
                continue
            self._datas_by_file[subdir].append(OtoRecord(subdir, filename, params[0], params[1], params[4], params[5], params[2], params[3]))
            self._setValue(params[0], self._datas_by_file[subdir][-1])
            self._setValue(".".join(os.path.join(subdir, filename).split(".")[:-1]), self._datas_by_file[subdir][-1])

