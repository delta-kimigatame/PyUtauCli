# PyUtauCli

### これは何?
* 飴屋／菖蒲氏によって公開されている、Windows向けに作成された歌声合成ソフトウェア「UTAU」関連データを扱うプロジェクトです。

    UTAU公式サイト(http://utau2008.web.fc2.com/)

* 扱えるデータ

  * .ustファイル(UTAU sequence txt) 
    * ust version1.2に限る
    * ヘッダ部分の文字コードはシステム既定もしくはcp932
    * body部分の文字コードはcp932もしくはutf-8
  * utauplugin用データ
  * UTAU音源関連データ
    * oto.ini
    * prefix.map
    * .frq(周波数表データ)
  * windows版UTAUの設定ファイル

* 改造や組み込みを歓迎しますが、それらのためのドキュメントは準備中です。
* 音声の合成には、下記の兄弟プロジェクトを活用しています。

    PyWavTool(https://github.com/delta-kimigatame/PyWavTool)
    PyRwu(https://github.com/delta-kimigatame/PyRwu)


***

### 免責事項
* 本ソフトウェアを使用して生じたいかなる不具合についても、作者は責任を負いません。
* 作者は、本ソフトウェアの不具合を修正する責任を負いません。

***

### モジュールの使い方
#### インストール
``` pip install PyUtauCli```


#### 使い方(ustファイルからwavを生成する)
```Python
from PyUtauCli.projects.Render import Render
from PyUtauCli.projects.Ust import Ust

#ustファイルの読み込み
ust = Ust("ustpath.ust")
ust.load()

#各種パラメータの変換
render = Render(ust, cache_dir="cache", output_file="output.wav")
#キャッシュの削除
render.clean()
#PyRwuを用いてキャッシュファイルの生成
render.resamp()
#キャッシュファイルを使用してoutput.wavの生成
render.append()
```

#### 使い方(ustプラグイン -選択ノートを半音上げるプラグイン-)
```Python
import sys
from PyUtauCli.projects.UtauPlugin import UtauPlugin

print(sys.argv)
#['plugin.py', 'C:\User\username\AppData\Local\Temp\utau1\tmp****.tmp']

#プラグインファイルの読み込み
plugin = UtauPlugin(sys.argv[1])
plugin.load()

#半音上げる処理
for note in plugin.notes:
    note.notenum.value += 1

#プラグインファイルの書き込み
plugin.save()
```
***

### 技術仕様
* ドキュメント(https://delta-kimigatame.github.io/PyUtauCli/index.html)

***

### リンク
* twitter(https://twitter.com/delta_kuro)
* github(https://github.com/delta-kimigatame/PyUtauCli)