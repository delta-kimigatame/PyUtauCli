# PyUtauCli

### ����͉�?
* �����^�Ҋ����ɂ���Č��J����Ă���AWindows�����ɍ쐬���ꂽ�̐������\�t�g�E�F�A�uUTAU�v�֘A�f�[�^�������v���W�F�N�g�ł��B

    UTAU�����T�C�g(http://utau2008.web.fc2.com/)

* ������f�[�^

  * .ust�t�@�C��(UTAU sequence txt) 
    * ust version1.2�Ɍ���
    * �w�b�_�����̕����R�[�h�̓V�X�e�������������cp932
    * body�����̕����R�[�h��cp932��������utf-8
  * utauplugin�p�f�[�^
  * UTAU�����֘A�f�[�^
    * oto.ini
    * prefix.map
    * .frq(���g���\�f�[�^)
  * windows��UTAU�̐ݒ�t�@�C��

* ������g�ݍ��݂����}���܂����A�����̂��߂̃h�L�������g�͏������ł��B
* �����̍����ɂ́A���L�̌Z��v���W�F�N�g�����p���Ă��܂��B

    PyWavTool(https://github.com/delta-kimigatame/PyWavTool)
    PyRwu(https://github.com/delta-kimigatame/PyRwu)


***

### �Ɛӎ���
* �{�\�t�g�E�F�A���g�p���Đ����������Ȃ�s��ɂ��Ă��A��҂͐ӔC�𕉂��܂���B
* ��҂́A�{�\�t�g�E�F�A�̕s����C������ӔC�𕉂��܂���B

***

### ���W���[���̎g����
#### �C���X�g�[��
``` pip install PyUtauCli```


#### �g����(ust�t�@�C������wav�𐶐�����)
```Python
from PyUtauCli.projects.Render import Render
from PyUtauCli.projects.Ust import Ust

#ust�t�@�C���̓ǂݍ���
ust = Ust("ustpath.ust")
ust.load()

#�e��p�����[�^�̕ϊ�
render = Render(ust, cache_dir="cache", output_file="output.wav")
#�L���b�V���̍폜
render.clean()
#PyRwu��p���ăL���b�V���t�@�C���̐���
render.resamp()
#�L���b�V���t�@�C�����g�p����output.wav�̐���
render.append()
```

#### �g����(ust�v���O�C�� -�I���m�[�g�𔼉��グ��v���O�C��-)
```Python
import sys
from PyUtauCli.projects.UtauPlugin import UtauPlugin

print(sys.argv)
#['plugin.py', 'C:\User\username\AppData\Local\Temp\utau1\tmp****.tmp']

#�v���O�C���t�@�C���̓ǂݍ���
plugin = UtauPlugin(sys.argv[1])
plugin.load()

#�����グ�鏈��
for note in plugin.notes:
    note.notenum.value += 1

#�v���O�C���t�@�C���̏�������
plugin.save()
```
***

### �Z�p�d�l
* �h�L�������g(https://delta-kimigatame.github.io/PyUtauCli/index.html)

***

### �����N
* twitter(https://twitter.com/delta_kuro)
* github(https://github.com/delta-kimigatame/PyUtauCli)