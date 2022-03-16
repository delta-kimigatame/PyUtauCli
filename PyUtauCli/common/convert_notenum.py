'''
音名と音階番号の変換を扱います。
'''
from typing import Literal

TONE_NUM: dict = {"C": 0, "C#": 1, "C♯": 1, "Db": 1, "D♭": 1,
                  "D": 2, "D#": 3, "D♯": 3, "Eb": 3, "E♭": 3,
                  "E": 4,
                  "F": 5, "F#": 6, "F♯": 6, "Gb": 6, "G♭": 6,
                  "G": 7, "G#": 8, "G♯": 8, "Ab": 8, "A♭": 8,
                  "A": 9, "A#": 10, "A♯": 10, "Bb": 10, "B♭": 10,
                  "B": 11}

TONE_NAME: dict = {"#": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
                   "♯": ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"],
                   "b": ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"],
                   "♭": ["C", "D♭", "D", "E♭", "E", "F", "G♭", "G", "A♭", "A", "B♭", "B"],
                   }


def toInt(tone: str) -> int:
    '''
    音名をnotenumに変換します。

    Parameters
    ----------
    tone: str
        C4,C#4,Db3など、音名を表す文字列

    Returns
    -------
    notenum: int
        
        C1=24,C#1=25...B7=107のような整数

    Raises
    ------
    ValueError
        音名以外の文字列が与えられたとき
    '''
    try:
        return TONE_NUM[tone[:-1]] + (int(tone[-1]) + 1) * 12
    except:
        raise ValueError("{} is not tone-name.".format(tone))


def toStr(notenum: int, mark: Literal["#", "b", "＃", "♭"]="#") -> str:
    '''
    notenumを音名に変換します。

    Parameters
    ----------
    notenum: int
        C1=24,C#1=25...B7=107のような整数

    mark: Literal["#","b","＃","♭"], default "#"
        半音階をどのような文字であらわすか?

    Returns
    -------
    tone: str
        C4,C#4,Db3など、音名を表す文字列

    Raises
    ------
    ValueError
        markの値が不正な時

    '''
    try:
        return TONE_NAME[mark][notenum % 12] + str(notenum // 12 - 1)
    except:
        raise ValueError("{} is not sharp or flat.[#,b,♯,♭]".format(mark))
