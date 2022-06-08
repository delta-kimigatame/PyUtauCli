'''
entryおよびentrybaseモジュールのテスト
'''


import unittest
from unittest import mock

import os
import os.path

from projects.Entry import *
from projects.EntryBase import *

class TestEntryBase(unittest.TestCase):
    TestClass = EntryBase
    def test_set_update(self):
        e = self.TestClass()
        self.assertFalse(e.isUpdate)
        e._set_update()
        self.assertTrue(e.isUpdate)

    def test_has_data(self):
        e = self.TestClass()
        self.assertFalse(e.hasValue)

class TestStringEntry(TestEntryBase):
    TestClass = StringEntry
    def test_init(self):
        e = self.TestClass()
        e.init("test")
        self.assertEqual("test", e.value)
        self.assertTrue(e.hasValue)
        self.assertFalse(e.isUpdate)
        self.assertEqual(str(e), e.value)
        
    def test_change_value(self):
        e = self.TestClass()
        e.init("test")
        self.assertEqual("test", e.value)
        self.assertTrue(e.hasValue)
        self.assertFalse(e.isUpdate)
        self.assertEqual(str(e), e.value)
        e.value = "test2"
        self.assertEqual("test2", e.value)
        self.assertTrue(e.hasValue)
        self.assertTrue(e.isUpdate)
        self.assertEqual(str(e), e.value)
        
    def test_set_value(self):
        e = self.TestClass()
        e.value = "test2"
        self.assertEqual("test2", e.value)
        self.assertTrue(e.hasValue)
        self.assertTrue(e.isUpdate)
        self.assertEqual(str(e), e.value)

        
class TestIntEntry(TestEntryBase):
    TestClass = IntEntry
    def test_init(self):
        e = self.TestClass()
        e.init("1")
        self.assertEqual(1, e.value)
        self.assertTrue(e.hasValue)
        self.assertFalse(e.isUpdate)
        self.assertEqual(str(e), str(e.value))

    def test_init_bad_value(self):
        e = self.TestClass()
        
        with self.assertRaises(ValueError) as cm:
            e.init("a")
        self.assertEqual(cm.exception.args[0], "{} is not int".format("a"))
        self.assertFalse(e.hasValue)
        self.assertFalse(e.isUpdate)
        
    def test_change_value(self):
        e = self.TestClass()
        e.init("1")
        self.assertEqual(1, e.value)
        self.assertTrue(e.hasValue)
        self.assertFalse(e.isUpdate)
        self.assertEqual(str(e), str(e.value))
        e.value = "3"
        self.assertEqual(3, e.value)
        self.assertTrue(e.hasValue)
        self.assertTrue(e.isUpdate)
        self.assertEqual(str(e), str(e.value))
        
    def test_set_value(self):
        e = self.TestClass()
        e.value = "3"
        self.assertEqual(3, e.value)
        self.assertTrue(e.hasValue)
        self.assertTrue(e.isUpdate)
        self.assertEqual(str(e), str(e.value))
        
    def test_set_bad_value(self):
        e = self.TestClass()
        with self.assertRaises(ValueError) as cm:
            e.value = "a"
        self.assertEqual(cm.exception.args[0], "{} is not int".format("a"))
        self.assertFalse(e.hasValue)
        self.assertFalse(e.isUpdate)
        
class TestFloatEntry(TestEntryBase):
    TestClass = FloatEntry
    point = 3
    def test_init(self):
        e = self.TestClass()
        e.init("1")
        self.assertEqual(1.000, e.value)
        self.assertTrue(e.hasValue)
        self.assertFalse(e.isUpdate)
        print(self.point)
        self.assertEqual(str(e), ("{:."+str(self.point) + "f}").format(1))

    def test_init_bad_value(self):
        e = self.TestClass()
        
        with self.assertRaises(ValueError) as cm:
            e.init("a")
        self.assertEqual(cm.exception.args[0], "{} is not float".format("a"))
        self.assertFalse(e.hasValue)
        self.assertFalse(e.isUpdate)
        
    def test_change_value(self):
        e = self.TestClass()
        e.init("1")
        self.assertEqual(1.000, e.value)
        self.assertTrue(e.hasValue)
        self.assertFalse(e.isUpdate)
        self.assertEqual(str(e), ("{:."+str(self.point) + "f}").format(1))
        e.value = "3"
        self.assertEqual(3, e.value)
        self.assertTrue(e.hasValue)
        self.assertTrue(e.isUpdate)
        self.assertEqual(str(e), ("{:."+str(self.point) + "f}").format(3))
        
    def test_set_value(self):
        e = self.TestClass()
        e.value = "3"
        self.assertEqual(3, e.value)
        self.assertTrue(e.hasValue)
        self.assertTrue(e.isUpdate)
        self.assertEqual(str(e), ("{:."+str(self.point) + "f}").format(3))
        
    def test_set_bad_value(self):
        e = self.TestClass()
        with self.assertRaises(ValueError) as cm:
            e.value = "a"
        self.assertEqual(cm.exception.args[0], "{} is not float".format("a"))
        self.assertFalse(e.hasValue)
        self.assertFalse(e.isUpdate)

        
class TestBoolEntry(TestEntryBase):
    TestClass = BoolEntry
    def test_init(self):
        e = self.TestClass()
        e.init(True)
        self.assertTrue(e.value)
        self.assertTrue(e.hasValue)
        self.assertFalse(e.isUpdate)
        self.assertEqual(str(e), "True")
        
    def test_change_value(self):
        e = self.TestClass()
        e.init(True)
        self.assertTrue(e.value)
        self.assertTrue(e.hasValue)
        self.assertFalse(e.isUpdate)
        self.assertEqual(str(e), "True")
        e.value = False
        self.assertFalse(e.value)
        self.assertTrue(e.hasValue)
        self.assertTrue(e.isUpdate)
        self.assertEqual(str(e), "False")
        e.value = 1
        self.assertEqual(str(e), "True")
        e.value = 0
        self.assertEqual(str(e), "False")
        e.value = "a"
        self.assertEqual(str(e), "True")
        
    def test_set_value(self):
        e = self.TestClass()
        e.value = False
        self.assertFalse(e.value)
        self.assertTrue(e.hasValue)
        self.assertTrue(e.isUpdate)
        self.assertEqual(str(e), "False")

class TestListEntry(TestEntryBase):
    TestClass = ListEntry
    baselist = ["1","2","3"]
    changelist = ["4","5","6"]
    base_str = "1,2,3"
    change_str = "4,5,6"
    add_value = "4"
    append_result = "1,2,3,4"
    insert_result = "1,2,4,3"
    set_result = "1,2,4"
    pop_result = "1,3"
    append_result_list = ["1","2","3","4"]
    insert_result_list = ["1","2","4","3"]
    set_result_list = ["1","2","4"]
    pop_result_list = ["1","3"]
    def test_init(self):
        e = self.TestClass()
        e.init(self.baselist)
        self.assertListEqual(e.value, self.baselist)
        self.assertTrue(e.hasValue)
        self.assertFalse(e.isUpdate)
        self.assertEqual(str(e), self.base_str)
        
    def test_init_from_str(self):
        e = self.TestClass()
        e.init_from_str(self.base_str)
        self.assertListEqual(e.value, self.baselist)
        self.assertTrue(e.hasValue)
        self.assertFalse(e.isUpdate)
        self.assertEqual(str(e), self.base_str)
        
    def test_change(self):
        e = self.TestClass()
        e.init(self.baselist)
        self.assertListEqual(e.value, self.baselist)
        self.assertTrue(e.hasValue)
        self.assertFalse(e.isUpdate)
        self.assertEqual(str(e), self.base_str)
        e.value = self.changelist
        self.assertListEqual(e.value, self.changelist)
        self.assertTrue(e.hasValue)
        self.assertTrue(e.isUpdate)
        self.assertEqual(str(e), self.change_str)
        
    def test_setvalues(self):
        e = self.TestClass()
        e.value = self.changelist
        self.assertListEqual(e.value, self.changelist)
        self.assertTrue(e.hasValue)
        self.assertTrue(e.isUpdate)
        self.assertEqual(str(e), self.change_str)
        
    def test_append(self):
        e = self.TestClass()
        e.init(self.baselist)
        e.append(self.add_value)
        self.assertListEqual(e.value, self.append_result_list)
        self.assertTrue(e.hasValue)
        self.assertTrue(e.isUpdate)
        self.assertEqual(str(e), self.append_result)
        
    def test_insert(self):
        e = self.TestClass()
        e.init(self.baselist)
        e.insert(2, self.add_value)
        self.assertListEqual(e.value, self.insert_result_list)
        self.assertTrue(e.hasValue)
        self.assertTrue(e.isUpdate)
        self.assertEqual(str(e), self.insert_result)
        
    def test_set(self):
        e = self.TestClass()
        e.init(self.baselist)
        e.set(2,self.add_value)
        self.assertListEqual(e.value, self.set_result_list)
        self.assertTrue(e.hasValue)
        self.assertTrue(e.isUpdate)
        self.assertEqual(str(e), self.set_result)
        
    def test_pop(self):
        e = self.TestClass()
        e.init(self.baselist)
        e.pop(1)
        self.assertListEqual(e.value, self.pop_result_list)
        self.assertTrue(e.hasValue)
        self.assertTrue(e.isUpdate)
        self.assertEqual(str(e), self.pop_result)

class TestNumberEntry(TestStringEntry):
    TestClass = NumberEntry
    
class TestLyricEntry(TestStringEntry):
    TestClass = LyricEntry
    
class TestAtAliasEntry(TestStringEntry):
    TestClass = AtAliasEntry
    
class TestAtFileNameEntry(TestStringEntry):
    TestClass = AtFileNameEntry
    
class TestLabelEntry(TestStringEntry):
    TestClass = LabelEntry
    
class TestRegionEntry(TestStringEntry):
    TestClass = RegionEntry
    
class TestRegionEndEntry(TestStringEntry):
    TestClass = RegionEndEntry
    
class TestLengthEntry(TestIntEntry):
    TestClass = LengthEntry
    
class TestNoteNumEntry(TestIntEntry):
    TestClass = NoteNumEntry
    def test_set_tone_name(self):
        e = self.TestClass()
        e.init("1")
        self.assertEqual(1, e.value)
        self.assertTrue(e.hasValue)
        self.assertFalse(e.isUpdate)
        self.assertEqual(str(e), str(e.value))
        e.set_from_str("C4")
        self.assertEqual(60, e.value)
        self.assertTrue(e.hasValue)
        self.assertTrue(e.isUpdate)
        self.assertEqual(e.get_tone_name(), "C4")
        

class TestVelocityEntry(TestIntEntry):
    TestClass = VelocityEntry
    
class TestIntensityEntry(TestIntEntry):
    TestClass = IntensityEntry
    
class TestModurationEntry(TestIntEntry):
    TestClass = ModurationEntry
    
class TestTempoEntry(TestFloatEntry):
    TestClass = TempoEntry
    point = 2
    
class TestPreEntry(TestFloatEntry):
    TestClass = PreEntry
    
class TestAtPreEntry(TestFloatEntry):
    TestClass = AtPreEntry

class TestOveEntry(TestFloatEntry):
    TestClass = PreEntry
    
class TestAtOveEntry(TestFloatEntry):
    TestClass = AtPreEntry

class TestStpEntry(TestFloatEntry):
    TestClass = PreEntry
    
class TestAtStpEntry(TestFloatEntry):
    TestClass = AtPreEntry
    
class TestPBStartEntry(TestFloatEntry):
    TestClass = PBStartEntry
    
class TestDirectEntry(TestBoolEntry):
    TestClass = DirectEntry

class TestPitchesEntry(TestListEntry):
    TestClass = PitchesEntry
    baselist = [1,2,3]
    changelist = [4,5,6]
    base_str = "1,2,3"
    change_str = "4,5,6"
    add_value = 4
    append_result = "1,2,3,4"
    insert_result = "1,2,4,3"
    set_result = "1,2,4"
    pop_result = "1,3"
    append_result_list = [1,2,3,4]
    insert_result_list = [1,2,4,3]
    set_result_list = [1,2,4]
    pop_result_list = [1,3]
    def test_bad_init(self):
        e = self.TestClass()
        with self.assertRaises(ValueError) as cm:
            e.init(["a"])
        self.assertEqual(cm.exception.args[0], "{} is not int".format("a"))
        self.assertFalse(e.hasValue)
        self.assertFalse(e.isUpdate)
        
    def test_bad_init_from_str(self):
        e = self.TestClass()
        with self.assertRaises(ValueError) as cm:
            e.init_from_str("a,b")
        self.assertEqual(cm.exception.args[0], "{} is not int".format("a"))
        self.assertFalse(e.hasValue)
        self.assertFalse(e.isUpdate)

    def test_append_bad(self):
        e = self.TestClass()
        e.init(self.baselist)
        with self.assertRaises(ValueError) as cm:
            e.append("a")
        self.assertEqual(cm.exception.args[0], "{} is not int".format("a"))
        self.assertFalse(e.isUpdate)
        
    def test_insert_bad(self):
        e = self.TestClass()
        e.init(self.baselist)
        with self.assertRaises(ValueError) as cm:
            e.insert(3, "a")
        self.assertEqual(cm.exception.args[0], "{} is not int".format("a"))
        self.assertFalse(e.isUpdate)
        
    def test_set_bad(self):
        e = self.TestClass()
        e.init(self.baselist)
        with self.assertRaises(ValueError) as cm:
            e.set(3, "a")
        self.assertEqual(cm.exception.args[0], "{} is not int".format("a"))
        self.assertFalse(e.isUpdate)

    
class TestPBMEntry(TestListEntry):
    TestClass = PBMEntry
    baselist = ["","s","r"]
    changelist = ["j","r","s"]
    base_str = ",s,r"
    change_str = "j,r,s"
    add_value = "j"
    append_result = ",s,r,j"
    insert_result = ",s,j,r"
    set_result = ",s,j"
    pop_result = ",r"
    append_result_list = ["","s","r","j"]
    insert_result_list = ["","s","j","r"]
    set_result_list = ["","s","j"]
    pop_result_list = ["","r"]
    def test_bad_init(self):
        e = self.TestClass()
        with self.assertRaises(ValueError) as cm:
            e.init(["a"])
        self.assertEqual(cm.exception.args[0], "{} is not '',s,r,j".format("a"))
        self.assertFalse(e.hasValue)
        self.assertFalse(e.isUpdate)
        
    def test_bad_init_from_str(self):
        e = self.TestClass()
        with self.assertRaises(ValueError) as cm:
            e.init_from_str("a,b")
        self.assertEqual(cm.exception.args[0], "{} is not '',s,r,j".format("a"))
        self.assertFalse(e.hasValue)
        self.assertFalse(e.isUpdate)

    def test_append_bad(self):
        e = self.TestClass()
        e.init(self.baselist)
        with self.assertRaises(ValueError) as cm:
            e.append("a")
        self.assertEqual(cm.exception.args[0], "{} is not '',s,r,j".format("a"))
        self.assertFalse(e.isUpdate)
        
    def test_insert_bad(self):
        e = self.TestClass()
        e.init(self.baselist)
        with self.assertRaises(ValueError) as cm:
            e.insert(3, "a")
        self.assertEqual(cm.exception.args[0], "{} is not '',s,r,j".format("a"))
        self.assertFalse(e.isUpdate)
        
    def test_set_bad(self):
        e = self.TestClass()
        e.init(self.baselist)
        with self.assertRaises(ValueError) as cm:
            e.set(3, "a")
        self.assertEqual(cm.exception.args[0], "{} is not '',s,r,j".format("a"))
        self.assertFalse(e.isUpdate)
        
class TestPBYEntry(TestListEntry):
    TestClass = PBYEntry
    baselist = [1.1,2.1,3.1]
    changelist = [4.1,5.1,6.1]
    base_str = "1.1,2.1,3.1"
    change_str = "4.1,5.1,6.1"
    add_value = 4.1
    append_result = "1.1,2.1,3.1,4.1"
    insert_result = "1.1,2.1,4.1,3.1"
    set_result = "1.1,2.1,4.1"
    pop_result = "1.1,3.1"
    append_result_list = [1.1,2.1,3.1,4.1]
    insert_result_list = [1.1,2.1,4.1,3.1]
    set_result_list = [1.1,2.1,4.1]
    pop_result_list = [1.1,3.1]
    def test_bad_init(self):
        e = self.TestClass()
        with self.assertRaises(ValueError) as cm:
            e.init(["a"])
        self.assertEqual(cm.exception.args[0], "{} is not float".format("a"))
        self.assertFalse(e.hasValue)
        self.assertFalse(e.isUpdate)
        
    def test_bad_init_from_str(self):
        e = self.TestClass()
        with self.assertRaises(ValueError) as cm:
            e.init_from_str("a,b")
        self.assertEqual(cm.exception.args[0], "{} is not float".format("a"))
        self.assertFalse(e.hasValue)
        self.assertFalse(e.isUpdate)

    def test_append_bad(self):
        e = self.TestClass()
        e.init(self.baselist)
        with self.assertRaises(ValueError) as cm:
            e.append("a")
        self.assertEqual(cm.exception.args[0], "{} is not float".format("a"))
        self.assertFalse(e.isUpdate)
        
    def test_insert_bad(self):
        e = self.TestClass()
        e.init(self.baselist)
        with self.assertRaises(ValueError) as cm:
            e.insert(3, "a")
        self.assertEqual(cm.exception.args[0], "{} is not float".format("a"))
        self.assertFalse(e.isUpdate)
        
    def test_set_bad(self):
        e = self.TestClass()
        e.init(self.baselist)
        with self.assertRaises(ValueError) as cm:
            e.set(3, "a")
        self.assertEqual(cm.exception.args[0], "{} is not float".format("a"))
        self.assertFalse(e.isUpdate)
        
class TestPBWEntry(TestListEntry):
    TestClass = PBWEntry
    baselist = [1.1,2.1,3.1]
    changelist = [4.1,5.1,6.1]
    base_str = "1.1,2.1,3.1"
    change_str = "4.1,5.1,6.1"
    add_value = 4.1
    append_result = "1.1,2.1,3.1,4.1"
    insert_result = "1.1,2.1,4.1,3.1"
    set_result = "1.1,2.1,4.1"
    pop_result = "1.1,3.1"
    append_result_list = [1.1,2.1,3.1,4.1]
    insert_result_list = [1.1,2.1,4.1,3.1]
    set_result_list = [1.1,2.1,4.1]
    pop_result_list = [1.1,3.1]
    def test_bad_init(self):
        e = self.TestClass()
        with self.assertRaises(ValueError) as cm:
            e.init(["a"])
        self.assertEqual(cm.exception.args[0], "{} is not float".format("a"))
        self.assertFalse(e.hasValue)
        self.assertFalse(e.isUpdate)
        
    def test_bad_init_from_str(self):
        e = self.TestClass()
        with self.assertRaises(ValueError) as cm:
            e.init_from_str("a,b")
        self.assertEqual(cm.exception.args[0], "{} is not float".format("a"))
        self.assertFalse(e.hasValue)
        self.assertFalse(e.isUpdate)

    def test_append_bad(self):
        e = self.TestClass()
        e.init(self.baselist)
        with self.assertRaises(ValueError) as cm:
            e.append("a")
        self.assertEqual(cm.exception.args[0], "{} is not float".format("a"))
        self.assertFalse(e.isUpdate)
        
    def test_insert_bad(self):
        e = self.TestClass()
        e.init(self.baselist)
        with self.assertRaises(ValueError) as cm:
            e.insert(3, "a")
        self.assertEqual(cm.exception.args[0], "{} is not float".format("a"))
        self.assertFalse(e.isUpdate)
        
    def test_set_bad(self):
        e = self.TestClass()
        e.init(self.baselist)
        with self.assertRaises(ValueError) as cm:
            e.set(3, "a")
        self.assertEqual(cm.exception.args[0], "{} is not float".format("a"))
        self.assertFalse(e.isUpdate)

class TestPBSEntry(TestEntryBase):
    TestClass = PBSEntry
    

class TestEnvelopeEntry(TestEntryBase):
    TestClass = EnvelopeEntry

class TestVibratoEntry(TestEntryBase):
    TestClass = VibratoEntry