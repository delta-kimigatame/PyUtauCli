import os.path


class Character:
    '''Character.txtを扱います

    Attributes
    ----------
    name: str, default ""
        VBの名前、与えられないときはフォルダ名

    image: str, default ""
        アイコン画像のパス

    sample: str, default ""
        サンプル音声のパス

    author: str, default ""
        管理人名

    web: str, default ""
        webサイトurl

    version: str, default ""
        バージョン

    dirpath: str, default ""
        音源のルートのパス
    '''
    _name: str = ""
    image: str = ""
    sample: str = ""
    author: str = ""
    web: str = ""
    version: str = ""
    dirpath: str = ""

    @property
    def name(self) -> str:
        if self._name != "":
            return self._name
        elif self.dirpath == "":
            return ""
        else:
            return os.path.split(self.dirpath)[1]

    @name.setter
    def name(self, value):
        self._name = value

    def __init__(self, dirpath: str = ""):
        '''
        Parameters
        ----------
        dirpath: str, default ""
            音源のルートディレクトリのパス。引数が与えられている場合self.load(dirpath)を実行する。

        Raises
        ------
        FileNotFoundError
            read実行時character.txtが見つからなかった場合
        UnicodeDecodeError
            read実行時ファイルがcp932でも環境の文字コードでもなかった場合
        '''
        if dirpath != "":
            self.load(dirpath)
            
    def load(self, dirpath: str):
        '''
        *dirpath\\\\character.txt* を読み込んで各パラメータを更新する。

        Parameters
        ----------
        dirpath
            音源のルートディレクトリのパス

        Raises
        ------
        FileNotFoundError
            character.txtが見つからなかった場合
        UnicodeDecodeError
            ファイルがcp932でも環境の文字コードでもなかった場合
        '''
        filepath: str = os.path.join(dirpath, "character.txt")
        lines: list
        self.dirpath = dirpath
        if not os.path.isfile(filepath):
            raise FileNotFoundError("{} is not found.".format(filepath))

        try:
            with open(filepath, "r") as fr:
                lines = fr.read().replace("\r", "").split("\n")
        except:
            try:
                with open(filepath, "r", encoding="cp932") as fr:
                    lines = fr.read().replace("\r", "").split("\n")
            except UnicodeDecodeError as e:
                e.reason = "can't read character.txt. because required character encoding is system default or cp932"
                raise e
        key: str
        value: str
        for line in lines:
            if line == "":
                continue
            if "=" not in line and ":" not in line:
                continue
            if "=" in line:
                key, value = line.split("=")
            else:
                key = line.split(":")[0]
                value = ":".join(line.split(":")[1:])

            if key.lower() == "name":
                self._name = value
            elif key.lower() == "image":
                self.image = value
            elif key.lower() == "sample":
                self.sample = value
            elif key.lower() == "author":
                self.author = value
            elif key.lower() == "web":
                self.web = value
            elif key.lower() == "version":
                self.version = value

    def save(self, encoding: str="cp932"):
        '''
        *self.dirpath\\\\character.txt* を *encoding* で保存する。

        Parameters
        ----------
        encoding: str, default "cp932"
            
            | 保存する際の文字コード
            | UTAU本体のGUIを考えるとcp932が無難

        Raises
        ------
        OSError
            character.txtに書き込み権限がないとき
        UnicodeDecodeError
            パラメータをcp932に変換できなかったとき
        '''
        filepath: str = os.path.join(self.dirpath, "character.txt")
        with open(filepath, "w", encoding=encoding) as fw:
            if self._name != "":
                fw.write("name=" + self._name + "\r\n")
            if self.image != "":
                fw.write("image=" + self.image + "\r\n")
            if self.sample != "":
                fw.write("sample=" + self.sample + "\r\n")
            if self.author != "":
                fw.write("Author=" + self.author + "\r\n")
            if self.web != "":
                fw.write("Web=" + self.web + "\r\n")
            if self.version != "":
                fw.write("Version=" + self.version + "\r\n")
