# GPvMSM-気象庁数値予報データ AutoDownloader - Downscaler

http://database.rish.kyoto-u.ac.jp/arch/jmadata/

気象庁の数値予報データGPVのダウンロード・アップスケーリングを自動化したコードです。

GPvMSMや気象庁数値予報データに関するもっと詳しい情報は上記のリンクをご参照ください。

##

### 20231213
・ファイルのdir構造が変更されました。

・centerを追加しました。

・class DataDownscalerを一部変更しました（＊修正中）

### 20231220
・downscaleの定常動作を確認

・getYearSum Classを追加

・getYearSumの追加により、downscaleは一年合計データに対して実行されます。

・出力ncファイルに変数 max_value を追加 (降水量配列の最大値)

### 20231221
・GPvMSM_vsl_v.0.0.1の実行の結果に varibale nameが目盛りに表示されるように変更

・GPvMSM.pyの実行の際、ディレクトリを生成できるように変更

・.envの設定を一部変更

・config.pyを一部変更

・.env、config.py、GPvMSM.pyの一部の環境変数名を修正

##


ファイルのディレクトリ構造は以下のようになりますのでご参照ください。

```
GPvMSM_Beta
├─lib
├─nc
│  ├─GPvMSM
│  │  └─2015 
│  ├─GPvMSM_DownScaled
│  └─GPvMSM_year
├─plot
└─shp
```
