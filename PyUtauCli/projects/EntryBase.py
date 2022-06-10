'''EntryBase
各ノートパラメータ設定用のベースクラスを定義します。
'''


class EntryBase:
    '''
    エントリー用のベースクラスです。
    継承して使います。
    '''
    _isUpdate: bool = False
    _hasValue: bool = False

    def _set_update(self):
        self._isUpdate = True

    @property
    def isUpdate(self) -> bool:
        return self._isUpdate

    @property
    def hasValue(self) -> bool:
        return self._hasValue


class StringEntry(EntryBase):
    '''
    Str型のvalueをもつエントリー用のベースクラスです。
    継承して使います。
    '''
    _value: str = ""

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = str(value)
        self._set_update()
        self._hasValue = True

    def init(self, value: str):
        self._value = value
        self._hasValue = True

    def __str__(self) -> str:
        return self.value


class IntEntry(EntryBase):
    '''
    int型のvalueをもつエントリー用のベースクラスです。
    継承して使います。
    '''
    _value: int = 0

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int):
        try:
            self._value = int(value)
            self._set_update()
            self._hasValue = True
        except:
            raise ValueError("{} is not int".format(value))

    def init(self, value: int):
        try:
            self._value = int(value)
            self._hasValue = True
        except:
            raise ValueError("{} is not int".format(value))

    def __str__(self) -> str:
        return str(self.value)


class FloatEntry(EntryBase):
    '''
    float型のvalueをもつエントリー用のベースクラスです。
    継承して使います。
    '''
    _value: float = 0.0
    point: int = 3

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float):
        try:
            self._value = float(value)
            self._set_update()
            self._hasValue = True
        except:
            raise ValueError("{} is not float".format(value))

    def init(self, value: float):
        try:
            self._value = float(value)
            self._hasValue = True
        except:
            raise ValueError("{} is not float".format(value))

    def __str__(self) -> str:
        return ("{:." + str(self.point) + "f}").format(self._value)


class BoolEntry(EntryBase):
    '''
    bool型のvalueをもつエントリー用のベースクラスです。
    継承して使います。
    '''
    _value: bool = False

    @property
    def value(self) -> bool:
        return bool(self._value)

    @value.setter
    def value(self, value: bool):
        self._value = bool(value)
        self._set_update()
        self._hasValue = True

    def init(self, value: bool):
        self._value = value
        self._hasValue = True

    def __str__(self) -> str:
        return str(self.value)


class ListEntry(EntryBase):
    '''
    list型のvalueをもつエントリー用のベースクラスです。
    継承して使います。
    各パラメータのフォーマットが適切かは、self._checl_valueを継承して定義します。
    '''
    _value: list = []
    separater: str = ","

    @property
    def value(self) -> list:
        return self._value

    @value.setter
    def value(self, value: list):
        for v in value:
            self._check_value(v)
        self._value = value
        self._set_update()
        self._hasValue = True

    def _check_value(self, value):
        '''
        Raises
        ------
        ValueError
            値が不適切な時
        '''
        return value

    def init(self, value: list):
        for v in value:
            v = self._check_value(v)
        self._value = value[:]
        self._hasValue = True

    def init_from_str(self, value: str):
        values: list = value.split(self.separater)
        for i in range(len(values)):
            values[i] = self._check_value(values[i])
        self._value = values[:]
        self._hasValue = True

    def __str__(self) -> str:
        return self.separater.join(map(str, self.value))

    def append(self, value):
        value = self._check_value(value)
        self._value.append(value)
        self._isUpdate = True

    def insert(self, pos: int, value):
        value = self._check_value(value)
        self._value.insert(pos, value)
        self._isUpdate = True

    def pop(self, pos: int):
        self._value.pop(pos)
        self._isUpdate = True

    def set(self, pos: int, value):
        value = self._check_value(value)
        self._value[pos] = value
        self._isUpdate = True
