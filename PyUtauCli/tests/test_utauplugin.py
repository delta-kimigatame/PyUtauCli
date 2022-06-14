'''
| projects.UtauPluginモジュールのテスト
| 主要な機能はUstモジュールの継承のため、差分のみテストする。
'''

import unittest
from unittest import mock

import os
import os.path
import logging

import projects.UtauPlugin
import settings.logger


class TestWrite(unittest.TestCase):
    @mock.patch("os.path.isfile")
    def setUp(self, mock_isfile):
        mock_isfile.return_value = True
        self.test_logger = settings.logger.get_logger("TEST", True)
        self.plugin = projects.UtauPlugin.UtauPlugin("testpath", logger=self.test_logger)
        test_header = ["[#VERSION]",
                       "UST Version1.2",
                       "[#SETTING]",
                       "Tempo=150.00",
                       "Tracks=1",
                       "Project=test",
                       "VoiceDir=%VOICE%{}".format("aaa"),
                       "OutFile=output.wav",
                       "CacheDir=main__.cache",
                       "Tool1=wavtool.exe",
                       "Tool2=resamp.exe",
                       "Flags=B50",
                       "Mode2=True"]
        test_note = ["[#0000]",
                     "Length=1920",
                     "Lyric={}".format("あ"),
                     "NoteNum=60",
                     "PreUtterance="]
        test_note2 = ["[#0001]",
                      "Length=1920",
                      "Lyric={}".format("あ"),
                      "NoteNum=60",
                      "Tempo=120",
                      "PreUtterance=1",
                      "@preuttr=2",
                      "VoiceOverlap=3",
                      "@overlap=4",
                      "StartPoint=5",
                      "@stpoint=6",
                      "@filename=filepath",
                      "@alias=あ_C4",
                      "Velocity=150",
                      "Intensity=80",
                      "Modulation=30",
                      "Pitches=0,1,2,3",
                      "PBStart=-10.0",
                      "PBS=-5;3",
                      "PBY=1,2,3",
                      "PBW=10,20,30,40",
                      "PBM=,s,r,j,",
                      "Flags=g-5",
                      "VBR=1,2,3,4,5,6,7,8",
                      "Envelope=9,10,11,12,13,14,15,%,16,17,18",
                      "Label=aa",
                      "$direct=True",
                      "$region=1番",
                      "$region_end=イントロ",
                      ]
        test_note3 = ["[#0002]",
                      "Length=1920",
                      "Lyric={}".format("あ"),
                      "NoteNum=60",
                      "PreUtterance="]
        data = "\n".join(test_header + test_note + test_note2 + test_note3 + ["[#TRACKEND]"]).encode("cp932")
        mock_io = mock.mock_open(read_data=data)
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.load()

    def test_write_nochange(self):
        mock_io = mock.mock_open()
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "[#0002]\n")
        
    def test_write_change_length(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].length.value = 480
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "Length=480\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")
        
    def test_write_change_lyric(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].lyric.value = "い"
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "Lyric=い\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_notenum(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].notenum.value = 61
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "NoteNum=61\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_tempo(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].tempo.value = 121
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "Tempo=121.00\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_pre(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].pre.value = 3
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "PreUtterance=3.000\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_ove(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].ove.value = 5
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "VoiceOverlap=5.000\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_stp(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].stp.value = 7
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "StartPoint=7.000\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_velocity(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].velocity.value = 0
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "Velocity=0\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_intensity(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].intensity.value = 0
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "Intensity=0\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_modulation(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].modulation.value = 0
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "Modulation=0\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_pitches(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].pitches.value = [0]
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "Pitches=0\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_pbstart(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].pbStart.value = 7
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "PBStart=7.000\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_pbs(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].pbs.value = "7"
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "PBS=7.000\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_pby(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].pby.value = ["7"]
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "PBY=7\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_pbw(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].pbw.value = ["7"]
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "PBW=7\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_pbm(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].pbm.value = [""]
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "PBM=\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_flags(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].flags.value = "B50"
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "Flags=B50\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_vibrato(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].vibrato.value = "2,3,4,5,6,7,8,9"
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "VBR=2.00,3.00,4.00,5.00,6.00,7.00,8.00,9.00\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_envelope(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].envelope.value = "1,2,3,4,5,6,7"
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "Envelope=1.00,2.00,3.00,4,5,6,7\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")

    def test_write_change_label(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].label.value = "bb"
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "Label=bb\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")
        
    def test_write_change_direct(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].direct.value = False
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "$direct=False\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")
        
    def test_write_change_region(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].region.value = "aa"
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "$region=aa\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")
        
    def test_write_change_region_end(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].region_end.value = "aa"
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "$region_end=aa\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "[#0002]\n")
        
    def test_write_change_all(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].length.value = 480
        self.plugin.notes[1].lyric.value = "い"
        self.plugin.notes[1].notenum.value = 61
        self.plugin.notes[1].tempo.value = 121
        self.plugin.notes[1].pre.value = 3
        self.plugin.notes[1].ove.value = 5
        self.plugin.notes[1].stp.value = 7
        self.plugin.notes[1].velocity.value = 0
        self.plugin.notes[1].intensity.value = 0
        self.plugin.notes[1].modulation.value = 0
        self.plugin.notes[1].pbStart.value = 7
        self.plugin.notes[1].pitches.value = [0]
        self.plugin.notes[1].pbs.value = "7"
        self.plugin.notes[1].pby.value = ["7"]
        self.plugin.notes[1].pbw.value = ["7"]
        self.plugin.notes[1].pbm.value = [""]
        self.plugin.notes[1].flags.value = "B50"
        self.plugin.notes[1].vibrato.value = "2,3,4,5,6,7,8,9"
        self.plugin.notes[1].envelope.value = "1,2,3,4,5,6,7"
        self.plugin.notes[1].label.value = "bb"
        self.plugin.notes[1].direct.value = False
        self.plugin.notes[1].region.value = "aa"
        self.plugin.notes[1].region_end.value = "aa"
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#0001]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "Length=480\n")
        self.assertEqual(mock_io().write.call_args_list[3][0][0], "Lyric=い\n")
        self.assertEqual(mock_io().write.call_args_list[4][0][0], "NoteNum=61\n")
        self.assertEqual(mock_io().write.call_args_list[5][0][0], "Tempo=121.00\n")
        self.assertEqual(mock_io().write.call_args_list[6][0][0], "PreUtterance=3.000\n")
        self.assertEqual(mock_io().write.call_args_list[7][0][0], "VoiceOverlap=5.000\n")
        self.assertEqual(mock_io().write.call_args_list[8][0][0], "StartPoint=7.000\n")
        self.assertEqual(mock_io().write.call_args_list[9][0][0], "Velocity=0\n")
        self.assertEqual(mock_io().write.call_args_list[10][0][0], "Intensity=0\n")
        self.assertEqual(mock_io().write.call_args_list[11][0][0], "Modulation=0\n")
        self.assertEqual(mock_io().write.call_args_list[12][0][0], "Pitches=0\n")
        self.assertEqual(mock_io().write.call_args_list[13][0][0], "PBStart=7.000\n")
        self.assertEqual(mock_io().write.call_args_list[14][0][0], "PBS=7.000\n")
        self.assertEqual(mock_io().write.call_args_list[15][0][0], "PBY=7\n")
        self.assertEqual(mock_io().write.call_args_list[16][0][0], "PBM=\n")
        self.assertEqual(mock_io().write.call_args_list[17][0][0], "PBW=7\n")
        self.assertEqual(mock_io().write.call_args_list[18][0][0], "Flags=B50\n")
        self.assertEqual(mock_io().write.call_args_list[19][0][0], "VBR=2.00,3.00,4.00,5.00,6.00,7.00,8.00,9.00\n")
        self.assertEqual(mock_io().write.call_args_list[20][0][0], "Envelope=1.00,2.00,3.00,4,5,6,7\n")
        self.assertEqual(mock_io().write.call_args_list[21][0][0], "Label=bb\n")
        self.assertEqual(mock_io().write.call_args_list[22][0][0], "$direct=False\n")
        self.assertEqual(mock_io().write.call_args_list[23][0][0], "$region=aa\n")
        self.assertEqual(mock_io().write.call_args_list[24][0][0], "$region_end=aa\n")
        self.assertEqual(mock_io().write.call_args_list[25][0][0], "[#0002]\n")
        
    def test_write_change_all_and_delete(self):
        mock_io = mock.mock_open()
        self.plugin.notes[1].num.value = "#DELETE"
        self.plugin.notes[1].length.value = 480
        self.plugin.notes[1].lyric.value = "い"
        self.plugin.notes[1].notenum.value = 61
        self.plugin.notes[1].tempo.value = 121
        self.plugin.notes[1].pre.value = 3
        self.plugin.notes[1].ove.value = 5
        self.plugin.notes[1].stp.value = 7
        self.plugin.notes[1].velocity.value = 0
        self.plugin.notes[1].intensity.value = 0
        self.plugin.notes[1].modulation.value = 0
        self.plugin.notes[1].pbStart.value = 7
        self.plugin.notes[1].pitches.value = [0]
        self.plugin.notes[1].pbs.value = "7"
        self.plugin.notes[1].pby.value = ["7"]
        self.plugin.notes[1].pbw.value = ["7"]
        self.plugin.notes[1].pbm.value = [""]
        self.plugin.notes[1].flags.value = "B50"
        self.plugin.notes[1].vibrato.value = "2,3,4,5,6,7,8,9"
        self.plugin.notes[1].envelope.value = "1,2,3,4,5,6,7"
        self.plugin.notes[1].label.value = "bb"
        self.plugin.notes[1].direct.value = False
        self.plugin.notes[1].region.value = "aa"
        self.plugin.notes[1].region_end.value = "aa"
        with self.assertLogs(logger=self.test_logger, level=logging.DEBUG) as logcm:
            with mock.patch("builtins.open", mock_io) as mocked_open:
                self.plugin.save()
        self.assertEqual(mock_io().write.call_args_list[0][0][0], "[#0000]\n")
        self.assertEqual(mock_io().write.call_args_list[1][0][0], "[#DELETE]\n")
        self.assertEqual(mock_io().write.call_args_list[2][0][0], "[#0002]\n")