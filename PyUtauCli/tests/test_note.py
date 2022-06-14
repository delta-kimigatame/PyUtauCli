'''
projects.Noteモジュールのテスト
'''

from sys import prefix
import unittest
from unittest import mock

import os
import os.path
import wave

import projects.Note
import voicebank.oto
import voicebank.prefixmap


class TestNote(unittest.TestCase):
    def test_init(self):
        n = projects.Note.Note()
        self.assertFalse(n.num.hasValue)
        self.assertFalse(n.length.hasValue)
        self.assertFalse(n.lyric.hasValue)
        self.assertFalse(n.notenum.hasValue)
        self.assertFalse(n.tempo.hasValue)
        self.assertFalse(n.pre.hasValue)
        self.assertFalse(n.atPre.hasValue)
        self.assertFalse(n.ove.hasValue)
        self.assertFalse(n.atOve.hasValue)
        self.assertFalse(n.stp.hasValue)
        self.assertFalse(n.atStp.hasValue)
        self.assertFalse(n.atFileName.hasValue)
        self.assertFalse(n.atAlias.hasValue)
        self.assertFalse(n.velocity.hasValue)
        self.assertFalse(n.intensity.hasValue)
        self.assertFalse(n.modulation.hasValue)
        self.assertFalse(n.pitches.hasValue)
        self.assertFalse(n.pbStart.hasValue)
        self.assertFalse(n.pbs.hasValue)
        self.assertFalse(n.pby.hasValue)
        self.assertFalse(n.pbm.hasValue)
        self.assertFalse(n.pbw.hasValue)
        self.assertFalse(n.envelope.hasValue)
        self.assertFalse(n.vibrato.hasValue)
        self.assertFalse(n.label.hasValue)
        self.assertFalse(n.direct.hasValue)
        self.assertFalse(n.region.hasValue)
        self.assertFalse(n.region_end.hasValue)
        self.assertFalse(n.flags.hasValue)
        self.assertIsNone(n.prev)
        self.assertIsNone(n.next)
        self.assertEqual(n.length.value, 480)
        self.assertEqual(n.notenum.value, 60)
        self.assertEqual(n.tempo.value, 120)
        self.assertEqual(n.velocity.value, 100)
        self.assertEqual(n.intensity.value, 100)
        self.assertEqual(n.modulation.value, 100)

    def test_msLength(self):
        n = projects.Note.Note()
        n.length.value = 480
        n.tempo.value = 120

        self.assertEqual(n.msLength, 500)
        n.length.value = 240
        self.assertEqual(n.msLength, 250)
        n.tempo.value = 60
        self.assertEqual(n.msLength, 500)

    def test_msLength_notInitial(self):
        n = projects.Note.Note()
        with self.assertRaises(ValueError) as cm:
            a = n.msLength
        self.assertEqual(cm.exception.args[0], "length is not initial")
        n.length.value = 480
        #with self.assertRaises(ValueError) as cm:
        #    a = n.msLength
        #self.assertEqual(cm.exception.args[0], "tempo is not initial")
        n.tempo.value = 120
        self.assertEqual(n.msLength, 500)


class TestNoteWithOto(unittest.TestCase):
    def setUp(self):
        self.oto = voicebank.oto.Oto()
        record1 = voicebank.oto.OtoRecord("subdir", "foo.wav", "test1", 100, 600, 200, 900, -1000)
        record2 = voicebank.oto.OtoRecord("", "foo1.wav", "test2", 100, 300, 100, 900, -1000)
        record3 = voicebank.oto.OtoRecord("subdir", "foo2.wav", "test1_C4", 100, 1200, 400, 900, -1000)
        self.oto._setValue("test1", record1)
        self.oto._setValue("test2", record2)
        self.oto._setValue("test1_C4", record3)
        self.prefix = voicebank.prefixmap.PrefixMap()
        self.prefix["C4"].suffix = "_C4"
        self.prefix["C#4"].suffix = "_C4"
        self.prefix["C#4"].prefix = "subdir\\"
        self.n = projects.Note.Note()

    def test_init_alias_with_atalias(self):
        self.n.lyric.value = "test2"
        self.n.notenum.value = 60
        self.n.atAlias.value = "test1"
        alias = self.n._init_alias(self.oto, self.prefix)
        self.assertEqual(alias, "test1")
        self.assertEqual(self.n.atAlias.value, "test1")

    def test_init_alias_with_prefixmap(self):
        self.n.lyric.value = "test1"
        self.n.notenum.value = 60
        alias = self.n._init_alias(self.oto, self.prefix)
        self.assertEqual(alias, "test1_C4")
        self.assertEqual(self.n.atAlias.value, "test1_C4")
        self.assertEqual(self.n.atFileName.value, "subdir\\foo2.wav")

    def test_init_alias_with_prefixmap_halfmatch(self):
        self.n.lyric.value = "test1"
        self.n.notenum.value = 61
        alias = self.n._init_alias(self.oto, self.prefix)
        self.assertEqual(alias, "test1")
        self.assertEqual(self.n.atAlias.value, "test1")
        self.assertEqual(self.n.atFileName.value, "subdir\\foo.wav")

    def test_init_alias_without_prefixmap(self):
        self.n.lyric.value = "test2"
        self.n.notenum.value = 60
        alias = self.n._init_alias(self.oto, self.prefix)
        self.assertEqual(alias, "test2")
        self.assertEqual(self.n.atAlias.value, "test2")
        self.assertEqual(self.n.atFileName.value, "foo1.wav")

    def test_init_alias_notfound(self):
        self.n.lyric.value = "test3"
        self.n.notenum.value = 60
        alias = self.n._init_alias(self.oto, self.prefix)
        self.assertEqual(alias, "")

    def test_apply_oto_to_pre_hasvalue(self):
        self.n.pre.value = 400
        self.assertTrue(self.n.pre.hasValue)
        self.n._apply_oto_to_pre("test1", self.oto)
        self.assertTrue(self.n.pre.value, 400)
        self.assertTrue(self.n.pre.hasValue)

    def test_apply_oto_to_pre_alias_notfound(self):
        self.assertFalse(self.n.pre.hasValue)
        self.n._apply_oto_to_pre("", self.oto)
        self.assertEqual(self.n.pre.value, 0)
        self.assertFalse(self.n.pre.hasValue)

    def test_apply_oto_to_pre_alias(self):
        self.assertFalse(self.n.pre.hasValue)
        self.n._apply_oto_to_pre("test1", self.oto)
        self.assertEqual(self.n.pre.value, 600)
        self.assertFalse(self.n.pre.hasValue)

    def test_apply_oto_to_ove_hasvalue(self):
        self.n.ove.value = 400
        self.assertTrue(self.n.ove.hasValue)
        self.n._apply_oto_to_ove("test1", self.oto)
        self.assertTrue(self.n.ove.value, 400)
        self.assertTrue(self.n.ove.hasValue)

    def test_apply_oto_to_ove_alias_notfound(self):
        self.assertFalse(self.n.ove.hasValue)
        self.n._apply_oto_to_ove("", self.oto)
        self.assertEqual(self.n.ove.value, 0)
        self.assertFalse(self.n.ove.hasValue)

    def test_apply_oto_to_ove_alias(self):
        self.assertFalse(self.n.ove.hasValue)
        self.n._apply_oto_to_ove("test1", self.oto)
        self.assertEqual(self.n.ove.value, 200)
        self.assertFalse(self.n.ove.hasValue)

    def test_autofit_prev_is_none(self):
        self.n.pre.value = 600
        self.n.ove.value = 200
        self.n.stp.value = 100
        self.n.autofit_atparam()
        self.assertTrue(self.n.atPre.hasValue)
        self.assertTrue(self.n.atOve.hasValue)
        self.assertTrue(self.n.atStp.hasValue)
        self.assertEqual(self.n.atPre.value, 600)
        self.assertEqual(self.n.atOve.value, 200)
        self.assertEqual(self.n.atStp.value, 100)

    def test_autofit_prev_is_not_initial(self):
        self.n.pre.value = 750
        self.n.ove.value = 250
        self.n.stp.value = 100
        prev = projects.Note.Note()
        self.n.prev = prev
        with self.assertRaises(ValueError) as cm:
            self.n.autofit_atparam()
        self.assertEqual(cm.exception.args[0], "prev lyric is not initial")
        prev.lyric.value = "あ"
        with self.assertRaises(ValueError) as cm:
            self.n.autofit_atparam()
        self.assertEqual(cm.exception.args[0], "length is not initial")
        prev.length.value = 960
        #with self.assertRaises(ValueError) as cm:
        #    self.n.autofit_atparam()
        #self.assertEqual(cm.exception.args[0], "tempo is not initial")
        prev.tempo.value = 120
        self.n.autofit_atparam()
        self.assertTrue(self.n.atPre.hasValue)
        self.assertTrue(self.n.atOve.hasValue)
        self.assertTrue(self.n.atStp.hasValue)
        self.assertEqual(self.n.atPre.value, 750)
        self.assertEqual(self.n.atOve.value, 250)
        self.assertEqual(self.n.atStp.value, 100)

    def test_autofit_prev_is_long(self):
        self.n.pre.value = 750
        self.n.ove.value = 250
        self.n.stp.value = 100
        prev = projects.Note.Note()
        prev.length.value = 960
        prev.tempo.value = 120
        prev.lyric.value = "あ"
        self.n.prev = prev
        self.n.autofit_atparam()
        self.assertTrue(self.n.atPre.hasValue)
        self.assertTrue(self.n.atOve.hasValue)
        self.assertTrue(self.n.atStp.hasValue)
        self.assertEqual(self.n.atPre.value, 750)
        self.assertEqual(self.n.atOve.value, 250)
        self.assertEqual(self.n.atStp.value, 100)

    def test_autofit_prev_is_short(self):
        self.n.pre.value = 750
        self.n.ove.value = 250
        self.n.stp.value = 100
        prev = projects.Note.Note()
        prev.length.value = 480
        prev.tempo.value = 120
        prev.lyric.value = "あ"
        self.n.prev = prev
        self.n.autofit_atparam()
        self.assertTrue(self.n.atPre.hasValue)
        self.assertTrue(self.n.atOve.hasValue)
        self.assertTrue(self.n.atStp.hasValue)
        self.assertEqual(self.n.atPre.value, 375)
        self.assertEqual(self.n.atOve.value, 125)
        self.assertEqual(self.n.atStp.value, 475)

    def test_autofit_prev_is_rest(self):
        self.n.pre.value = 750
        self.n.ove.value = 250
        self.n.stp.value = 100
        prev = projects.Note.Note()
        prev.length.value = 240
        prev.tempo.value = 120
        prev.lyric.value = "R"
        self.n.prev = prev
        self.n.autofit_atparam()
        self.assertTrue(self.n.atPre.hasValue)
        self.assertTrue(self.n.atOve.hasValue)
        self.assertTrue(self.n.atStp.hasValue)
        self.assertEqual(self.n.atPre.value, 375)
        self.assertEqual(self.n.atOve.value, 125)
        self.assertEqual(self.n.atStp.value, 475)

    def test_autofit_prev_with_velocity(self):
        self.n.pre.value = 1500
        self.n.ove.value = 500
        self.n.stp.value = 100
        self.n.velocity.value = 200
        prev = projects.Note.Note()
        prev.length.value = 480
        prev.tempo.value = 120
        prev.lyric.value = "あ"
        self.n.prev = prev
        self.n.autofit_atparam()
        self.assertTrue(self.n.atPre.hasValue)
        self.assertTrue(self.n.atOve.hasValue)
        self.assertTrue(self.n.atStp.hasValue)
        self.assertEqual(self.n.atPre.value, 375)
        self.assertEqual(self.n.atOve.value, 125)
        self.assertEqual(self.n.atStp.value, 425)

    def test_autofit_prev_with_velocity2(self):
        self.n.pre.value = 375
        self.n.ove.value = 125
        self.n.stp.value = 100
        self.n.velocity.value = 0
        prev = projects.Note.Note()
        prev.length.value = 480
        prev.tempo.value = 120
        prev.lyric.value = "あ"
        self.n.prev = prev
        self.n.autofit_atparam()
        self.assertTrue(self.n.atPre.hasValue)
        self.assertTrue(self.n.atOve.hasValue)
        self.assertTrue(self.n.atStp.hasValue)
        self.assertEqual(self.n.atPre.value, 375)
        self.assertEqual(self.n.atOve.value, 125)
        self.assertEqual(self.n.atStp.value, 575)

    def test_apply_oto(self):
        self.n.lyric.value = "test1"
        self.n.notenum.value = 61
        prev = projects.Note.Note()
        prev.length.value = 480
        prev.tempo.value = 120
        prev.lyric.value = "あ"
        self.n.prev = prev
        self.n.apply_oto(self.oto, self.prefix)
        self.assertEqual(self.n.pre.value, 600)
        self.assertEqual(self.n.ove.value, 200)
        self.assertFalse(self.n.pre.hasValue)
        self.assertFalse(self.n.ove.hasValue)
        self.assertEqual(self.n.atAlias.value, "test1")
        self.assertEqual(self.n.atFileName.value, "subdir\\foo.wav")
        self.assertEqual(self.n.atPre.value, 375)
        self.assertEqual(self.n.atOve.value, 125)
        self.assertEqual(self.n.atStp.value, 600 - 375)
        self.assertTrue(self.n.atPre.hasValue)
        self.assertTrue(self.n.atOve.hasValue)
        self.assertTrue(self.n.atStp.hasValue)

    def test_apply_oto_not_initialize(self):
        with self.assertRaises(ValueError) as cm:
            self.n.apply_oto(self.oto, self.prefix)
        self.assertEqual(cm.exception.args[0], "lyric is not initial")
        self.n.lyric.value = "test1"
        with self.assertRaises(ValueError) as cm:
            self.n.apply_oto(self.oto, self.prefix)
        self.assertEqual(cm.exception.args[0], "notenum is not initial")
        self.n.notenum.value = 61
