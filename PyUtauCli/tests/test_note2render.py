import unittest
from unittest import mock

import numpy as np
import PyRwu.pitch

import projects.Ust
import projects.Note
import projects.RenderNote
import voicebank
import voicebank.prefixmap
import voicebank.oto

class TestConvertPitch(unittest.TestCase):
    @mock.patch("voicebank.VoiceBank.is_utau_voicebank")
    def vb_load(self, dirpath , is_vb):
        is_vb.return_value = True
        return voicebank.VoiceBank("voice")

    def setUp(self):
        self.ust = projects.Ust.Ust("test")
        self.vb = self.vb_load("voice")
        self.oto = voicebank.oto.Oto()
        self.vb._oto = self.oto
        record1 = voicebank.oto.OtoRecord("", "foo.wav", "zero", 100, 0, 0, 900, -1000)
        record2 = voicebank.oto.OtoRecord("", "foo.wav", "simple", 100, 300, 100, 900, -1000)
        self.oto._setValue("zero", record1)
        self.oto._setValue("simple", record2)
        prev_note = projects.Note.Note()
        note = projects.Note.Note()
        next_note = projects.Note.Note()
        prev_note.num.value = "#0001"
        note.num.value = "#0002"
        next_note.num.value = "#0003"
        prev_note.length.value = 480
        note.length.value = 480
        next_note.length.value = 480
        prev_note.tempo.value = 100.0
        note.tempo.value = 100.0
        next_note.tempo.value = 100.0
        prev_note.lyric.value = "zero"
        note.lyric.value = "zero"
        next_note.lyric.value = "zero"
        prev_note.notenum.value = 58
        note.notenum.value = 60
        next_note.notenum.value = 62
        prev_note.envelope.value = "0,5,35,0,100,100,0"
        note.envelope.value = "0,5,35,0,100,100,0"
        next_note.envelope.value = "0,5,35,0,100,100,0"
        self.ust.notes.append(prev_note)
        self.ust.notes.append(note)
        self.ust.notes.append(next_note)

    def test_base_single_no_pbs(self):
        self.ust.notes[1].apply_oto(self.vb.oto, self.vb.prefix)
        self.assertEqual(self.ust.notes[1].atPre.value, 0)
        self.assertEqual(self.ust.notes[1].atStp.value, 0)
        r_note = projects.RenderNote.RenderNote(self.ust.notes[1], self.vb, "cache", "output", True)
        self.assertEqual(r_note._target_ms, 650)
        t = PyRwu.pitch.getPitchRange(100, 650, 44100)
        result = r_note._get_base_pitches(self.ust.notes[1], t)
        np.testing.assert_array_equal(result, np.zeros_like(t))
        
    def test_base_with_prev_no_pbs(self):
        self.ust.notes[1].prev = self.ust.notes[0]
        self.ust.notes[1].pre.value = 300
        self.ust.notes[0].apply_oto(self.vb.oto, self.vb.prefix)
        self.ust.notes[1].apply_oto(self.vb.oto, self.vb.prefix)
        self.assertEqual(self.ust.notes[1].atPre.value, 300)
        self.assertEqual(self.ust.notes[1].atStp.value, 0)
        r_note = projects.RenderNote.RenderNote(self.ust.notes[1], self.vb, "cache", "output", True)
        self.assertEqual(r_note._target_ms, 950)
        t = PyRwu.pitch.getPitchRange(100, 950, 44100)
        result = r_note._get_base_pitches(self.ust.notes[1], t)
        logical_result = np.zeros_like(t)
        logical_result[0:48-1] = -200
        np.testing.assert_array_equal(result, logical_result)
        self.assertEqual(result[46], -200)
        self.assertEqual(result[47], 0)
        
    def test_base_with_prev(self):
        self.ust.notes[1].prev = self.ust.notes[0]
        self.ust.notes[1].pre.value = 300
        self.ust.notes[1].pbs.value = "-150"
        self.ust.notes[0].apply_oto(self.vb.oto, self.vb.prefix)
        self.ust.notes[1].apply_oto(self.vb.oto, self.vb.prefix)
        self.assertEqual(self.ust.notes[1].atPre.value, 300)
        self.assertEqual(self.ust.notes[1].atStp.value, 0)
        r_note = projects.RenderNote.RenderNote(self.ust.notes[1], self.vb, "cache", "output", True)
        self.assertEqual(r_note._target_ms, 950)
        t = PyRwu.pitch.getPitchRange(100, 950, 44100)
        result = r_note._get_base_pitches(self.ust.notes[1], t)
        logical_result = np.zeros_like(t)
        logical_result[0:24-1] = -200
        np.testing.assert_array_equal(result, logical_result)
        self.assertEqual(result[22], -200)
        self.assertEqual(result[23], 0)
        
    def test_base_with_prev_and_rest(self):
        self.ust.notes[1].prev = self.ust.notes[0]
        self.ust.notes[1].pre.value = 300
        self.ust.notes[1].pbs.value = "-150"
        self.ust.notes[0].lyric.value = "R"
        self.ust.notes[0].apply_oto(self.vb.oto, self.vb.prefix)
        self.ust.notes[1].apply_oto(self.vb.oto, self.vb.prefix)
        self.assertEqual(self.ust.notes[1].atPre.value, 300)
        self.assertEqual(self.ust.notes[1].atStp.value, 0)
        r_note = projects.RenderNote.RenderNote(self.ust.notes[1], self.vb, "cache", "output", True)
        self.assertEqual(r_note._target_ms, 950)
        t = PyRwu.pitch.getPitchRange(100, 950, 44100)
        result = r_note._get_base_pitches(self.ust.notes[1], t)
        logical_result = np.zeros_like(t)
        np.testing.assert_array_equal(result, logical_result)
        
    def test_base_with_prev_pbs_positive(self):
        self.ust.notes[1].prev = self.ust.notes[0]
        self.ust.notes[1].pre.value = 300
        self.ust.notes[1].pbs.value = "150"
        self.ust.notes[0].apply_oto(self.vb.oto, self.vb.prefix)
        self.ust.notes[1].apply_oto(self.vb.oto, self.vb.prefix)
        self.assertEqual(self.ust.notes[1].atPre.value, 300)
        self.assertEqual(self.ust.notes[1].atStp.value, 0)
        r_note = projects.RenderNote.RenderNote(self.ust.notes[1], self.vb, "cache", "output", True)
        self.assertEqual(r_note._target_ms, 950)
        t = PyRwu.pitch.getPitchRange(100, 950, 44100)
        result = r_note._get_base_pitches(self.ust.notes[1], t)
        logical_result = np.zeros_like(t)
        logical_result[0:48+24-1] = -200
        np.testing.assert_array_equal(result, logical_result)
        self.assertEqual(result[48+24-2], -200)
        self.assertEqual(result[48+24-1], 0)
        
    def test_base_with_prev_stp(self):
        self.ust.notes[1].prev = self.ust.notes[0]
        self.ust.notes[1].stp.value = 300
        self.ust.notes[1].pbs.value = "-150"
        self.ust.notes[0].apply_oto(self.vb.oto, self.vb.prefix)
        self.ust.notes[1].apply_oto(self.vb.oto, self.vb.prefix)
        self.assertEqual(self.ust.notes[1].atPre.value, 0)
        self.assertEqual(self.ust.notes[1].atStp.value, 300)
        r_note = projects.RenderNote.RenderNote(self.ust.notes[1], self.vb, "cache", "output", True)
        self.assertEqual(r_note._target_ms, 950)
        t = PyRwu.pitch.getPitchRange(100, 950, 44100)
        result = r_note._get_base_pitches(self.ust.notes[1], t)
        logical_result = np.zeros_like(t)
        logical_result[0:24-1] = -200
        np.testing.assert_array_equal(result, logical_result)
        self.assertEqual(result[22], -200)
        self.assertEqual(result[23], 0)
        
        
    def test_base_with_prev_over_no_pbs(self):
        self.ust.notes[1].prev = self.ust.notes[0]
        self.ust.notes[1].pre.value = 300
        self.ust.notes[1].stp.value = 600
        self.ust.notes[0].apply_oto(self.vb.oto, self.vb.prefix)
        self.ust.notes[1].apply_oto(self.vb.oto, self.vb.prefix)
        self.assertEqual(self.ust.notes[1].atPre.value, 300)
        self.assertEqual(self.ust.notes[1].atStp.value, 600)
        r_note = projects.RenderNote.RenderNote(self.ust.notes[1], self.vb, "cache", "output", True)
        self.assertEqual(r_note._target_ms, 1550)
        t = PyRwu.pitch.getPitchRange(100, 1550, 44100)
        result = r_note._get_base_pitches(self.ust.notes[1], t)
        self.assertEqual(np.where(t >= self.ust.notes[0].pbs.time + 900 - self.ust.notes[0].msLength)[0][0], 48)
        self.assertEqual(np.where(t < self.ust.notes[1].pbs.time + 900)[0][-1],143)
        logical_result = np.zeros_like(t)
        logical_result[0:48] = 0
        logical_result[48:143] = -200
        np.testing.assert_array_equal(result, logical_result)

        
        
    def test_base_with_prev_over(self):
        self.ust.notes[1].prev = self.ust.notes[0]
        self.ust.notes[1].pre.value = 300
        self.ust.notes[1].stp.value = 600
        self.ust.notes[1].pbs.value = "-150"
        self.ust.notes[0].apply_oto(self.vb.oto, self.vb.prefix)
        self.ust.notes[1].apply_oto(self.vb.oto, self.vb.prefix)
        self.assertEqual(self.ust.notes[1].atPre.value, 300)
        self.assertEqual(self.ust.notes[1].atStp.value, 600)
        r_note = projects.RenderNote.RenderNote(self.ust.notes[1], self.vb, "cache", "output", True)
        self.assertEqual(r_note._target_ms, 1550)
        t = PyRwu.pitch.getPitchRange(100, 1550, 44100)
        self.assertEqual(np.where(t >= self.ust.notes[0].pbs.time + 900 - self.ust.notes[0].msLength)[0][0], 48)
        self.assertEqual(np.where(t < self.ust.notes[1].pbs.time + 900)[0][-1],119)
        result = r_note._get_base_pitches(self.ust.notes[1], t)
        logical_result = np.zeros_like(t)
        logical_result[0:48] = 0
        logical_result[48:119] = -200
        np.testing.assert_array_equal(result, logical_result)

        
    def test_base_with_prev_over_with_prev_pbs(self):
        self.ust.notes[1].prev = self.ust.notes[0]
        self.ust.notes[1].pre.value = 300
        self.ust.notes[1].stp.value = 600
        self.ust.notes[1].pbs.value = "-150"
        self.ust.notes[0].pbs.value = "-150"
        self.ust.notes[0].apply_oto(self.vb.oto, self.vb.prefix)
        self.ust.notes[1].apply_oto(self.vb.oto, self.vb.prefix)
        self.assertEqual(self.ust.notes[1].atPre.value, 300)
        self.assertEqual(self.ust.notes[1].atStp.value, 600)
        r_note = projects.RenderNote.RenderNote(self.ust.notes[1], self.vb, "cache", "output", True)
        self.assertEqual(r_note._target_ms, 1550)
        t = PyRwu.pitch.getPitchRange(100, 1550, 44100)
        self.assertEqual(np.where(t >= self.ust.notes[0].pbs.time + 900 - self.ust.notes[0].msLength)[0][0], 24)
        self.assertEqual(np.where(t < self.ust.notes[1].pbs.time + 900)[0][-1],119)
        result = r_note._get_base_pitches(self.ust.notes[1], t)
        logical_result = np.zeros_like(t)
        logical_result[0:24] = 0
        logical_result[24:119] = -200
        np.testing.assert_array_equal(result, logical_result)
        
    def test_base_with_prev_over_with_prev_pbs_over(self):
        self.ust.notes[1].prev = self.ust.notes[0]
        self.ust.notes[1].pre.value = 300
        self.ust.notes[1].stp.value = 600
        self.ust.notes[1].pbs.value = "-150"
        self.ust.notes[0].pbs.value = "-450"
        self.ust.notes[0].apply_oto(self.vb.oto, self.vb.prefix)
        self.ust.notes[1].apply_oto(self.vb.oto, self.vb.prefix)
        self.assertEqual(self.ust.notes[1].atPre.value, 300)
        self.assertEqual(self.ust.notes[1].atStp.value, 600)
        r_note = projects.RenderNote.RenderNote(self.ust.notes[1], self.vb, "cache", "output", True)
        self.assertEqual(r_note._target_ms, 1550)
        t = PyRwu.pitch.getPitchRange(100, 1550, 44100)
        self.assertEqual(np.where(t >= self.ust.notes[0].pbs.time + 900 - self.ust.notes[0].msLength)[0][0], 0)
        self.assertEqual(np.where(t < self.ust.notes[1].pbs.time + 900)[0][-1],119)
        result = r_note._get_base_pitches(self.ust.notes[1], t)
        logical_result = np.zeros_like(t)
        logical_result[0:119] = -200
        np.testing.assert_array_equal(result, logical_result)
        
    def test_base_with_next_no_pbs(self):
        self.ust.notes[1].next = self.ust.notes[2]
        self.ust.notes[1].pre.value = 300
        self.ust.notes[1].apply_oto(self.vb.oto, self.vb.prefix)
        self.ust.notes[2].apply_oto(self.vb.oto, self.vb.prefix)
        self.assertEqual(self.ust.notes[1].atPre.value, 300)
        self.assertEqual(self.ust.notes[1].atStp.value, 0)
        r_note = projects.RenderNote.RenderNote(self.ust.notes[1], self.vb, "cache", "output", True)
        self.assertEqual(r_note._target_ms, 950)
        t = PyRwu.pitch.getPitchRange(100, 950, 44100)
        result = r_note._get_base_pitches(self.ust.notes[1], t)
        logical_result = np.zeros_like(t)
        self.assertEqual(np.where(t >= self.ust.notes[2].pbs.time + 300 + self.ust.notes[1].msLength)[0][0],48+96)
        logical_result[48+96:] = 200
        np.testing.assert_array_equal(result, logical_result)
        
    def test_base_with_next(self):
        self.ust.notes[1].next = self.ust.notes[2]
        self.ust.notes[1].pre.value = 300
        self.ust.notes[2].pbs.value = "-150"
        self.ust.notes[1].apply_oto(self.vb.oto, self.vb.prefix)
        self.ust.notes[2].apply_oto(self.vb.oto, self.vb.prefix)
        self.assertEqual(self.ust.notes[1].atPre.value, 300)
        self.assertEqual(self.ust.notes[1].atStp.value, 0)
        r_note = projects.RenderNote.RenderNote(self.ust.notes[1], self.vb, "cache", "output", True)
        self.assertEqual(r_note._target_ms, 950)
        t = PyRwu.pitch.getPitchRange(100, 950, 44100)
        result = r_note._get_base_pitches(self.ust.notes[1], t)
        logical_result = np.zeros_like(t)
        self.assertEqual(np.where(t >= self.ust.notes[2].pbs.time + 300 + self.ust.notes[1].msLength)[0][0],48+96-24)
        logical_result[48+96-24:] = 200
        np.testing.assert_array_equal(result, logical_result)
