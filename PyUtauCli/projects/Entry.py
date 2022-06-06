from .EntryBase import EntryBase, IntEntry, StringEntry, FloatEntry, BoolEntry, ListEntry
import common.convert_notenum

class NumberEntry(StringEntry):
    pass

class LengthEntry(IntEntry):
    pass

class LyricEntry(StringEntry):
    pass

class NoteNumEntry(IntEntry):
    def set_from_str(self, value:str):
        self.value = common.convert_notenum.toInt(value)
        self._set_update()
        self._hasValue = True

    def get_tone_name(self) -> str:
        return common.convert_notenum.toStr(self.value)

class TempoEntry(FloatEntry):
    point = 2

class PreEntry(FloatEntry):
    pass

class AtPreEntry(FloatEntry):
    pass

class OveEntry(FloatEntry):
    pass

class AtOveEntry(FloatEntry):
    pass

class SttpEntry(FloatEntry):
    pass

class AtStpEntry(FloatEntry):
    pass

class AtFileNameEntry(StringEntry):
    pass

class AtAliasEntry(StringEntry):
    pass

class VelocityEntry(IntEntry):
    pass

class IntensityEntry(IntEntry):
    pass

class ModurationEntry(IntEntry):
    pass

class PitchesEntry(ListEntry):
    def _check_value(self, value):
        try:
            int(value)
        except:
            raise ValueError("{} is not int".format(value))

class PBStartEntry(FloatEntry):
    pass

class PBSEntry(EntryBase):
    _time: float
    _height: float
    _value: str

    @property
    def time(self) -> float:
        return self._time

    @property
    def height(self) -> float:
        return self._height

    @property
    def value(self) -> str:
        return self._value

    @time.setter
    def time(self, value: float):
        try:
            self._time = float(value)
            self._value = "{:.3f};{:.3f}".format(self._time, self._height)
            self._set_update()
            self._hasValue = True
        except:
            raise ValueError("{} is not float".format(value))

    @height.setter
    def height(self, value: float):
        try:
            self._height = float(value)
            self._value = "{:.3f};{:.3f}".format(self._time, self._height)
            self._set_update()
            self._hasValue = True
        except:
            raise ValueError("{} is not float".format(value))

    @value.setter
    def value(self, value: str):
        value = value.replace(",", ";")
        if ";" in value:
            values: list = value.split(";")
            try:
                self._time = float(values[0])
            except:
                raise ValueError("{} is not float".format(values[0]))
            try:
                self._height = float(values[1])
            except:
                raise ValueError("{} is not float".format(values[1]))
            self._value = value
            self._set_update()
            self._hasValue = True
        else:
            try:
                self._time = float(value)
            except:
                raise ValueError("{} is not float".format(value))
            self._value = value
            self._set_update()
            self._hasValue = True

    def init(self, value: str):
        value = value.replace(",", ";")
        if ";" in value:
            values: list = value.split(";")
            try:
                self._time = float(values[0])
            except:
                raise ValueError("{} is not float".format(values[0]))
            try:
                self._height = float(values[1])
            except:
                raise ValueError("{} is not float".format(values[1]))
            self._value = value
            self._hasValue = True
        else:
            try:
                self._time = float(value)
            except:
                raise ValueError("{} is not float".format(value))
            self._value = value
            self._hasValue = True

    def __str__(self) -> str:
        if self._height == 0:
            return "{:.3f}".format(self._time)
        else:
            return self._value


class PBYEntry(ListEntry):
    def _check_value(self, value):
        try:
            float(value)
        except:
            raise ValueError("{} is not float".format(value))
        
class PBWEntry(ListEntry):
    def _check_value(self, value):
        try:
            float(value)
        except:
            raise ValueError("{} is not float".format(value))
        
class PBMEntry(ListEntry):
    def _check_value(self, value):
        if value in ["", "s", "r", "j"]:
            str(value)
        else:
            raise ValueError("{} is not '',s,r,j".format(value))

class EnvelopeEntry(EntryBase):
    '''TODO
    '''
    pass

class VibratoEntry(EntryBase):
    '''TODO
    '''
    pass

class LabelEntry(StringEntry):
    pass

class DirectEntry(BoolEntry):
    pass


class RegionEntry(StringEntry):
    pass


class RegionEndEntry(StringEntry):
    pass
