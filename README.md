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

##


ファイルのディレクトリ構造は以下のようになりますのでご参照ください。

```
├─lib
├─nc
│  ├─GPvMSM
│  │  └─2015 
│  ├─GPvMSM_DownScaled
│  └─GPvMSM_year
├─plot
└─shp
```