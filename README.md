<h1 align="center">GPv-MSM AutoDownloader - Downscaler</h1>
<em><h5 align="center">(Programming Language - Python 3)</h5></em>

<p align="center">

<p align="center">
<a href="#"><img alt="GPvMSM_Beta forks" src="https://img.shields.io/github/forks/refiaa/GPvMSM_Beta?style=for-the-badge"></a>
<a href="#"><img alt="GPvMSM_Beta last commit (main)" src="https://img.shields.io/github/last-commit/refiaa/GPvMSM_Beta/main?color=green&style=for-the-badge"></a>
<a href="#"><img alt="GPvMSM_Beta Repo stars" src="https://img.shields.io/github/stars/refiaa/GPvMSM_Beta?style=for-the-badge&color=yellow"></a>
<a href="#"><img alt="GPvMSM_Beta License" src="https://img.shields.io/github/license/refiaa/GPvMSM_Beta?color=orange&style=for-the-badge"></a>
<a href="https://github.com/refiaa/GPvMSM_Beta/issues"><img alt="GPvMSM_Beta issues" src="https://img.shields.io/github/issues/refiaa/GPvMSM_Beta?color=purple&style=for-the-badge"></a>

http://database.rish.kyoto-u.ac.jp/arch/jmadata/

気象庁の数値予報データGPVのダウンロード・集計・ダウンスケーリングを自動化したコードです。
GPvMSMや気象庁数値予報データに関するもっと詳しい情報は上記のリンクをご参照ください。

YYYY.ncは一年間の日単位データです。

YYYY_sum.ncは一年合計雨量データです。

YYYY_DOWNSCALING_METHOD.ncはダウンスケーリングデータです。

**Clone and Install Script**

```shell script
git clone https://github.com/refiaa/GPvMSM_Beta.git
cd GPvMSM_Beta
pip install -r requirements.txt
```


**File Tree Structure**

ファイルのディレクトリ構造は以下のようになりますのでご参照ください。
```shell script
GPvMSM_Beta
├─lib
├─nc
│  ├─GPvMSM
│  │  └─YYYY             # YYYYMMDD.nc
│  ├─GPvMSM_DownScaled   # YYYY_DOWNSCALING_METHOD.nc
│  └─GPvMSM_year         # YYYY.nc, YYYY_sum.nc
├─plot                   # YYYY_DOWNSCALING_METHOD.png
└─shp
```

 ## 実行結果
 <em><h5 align="left">Grid Size 0.50°×0.50°, Using Median for DOWNSCALING_METHOD</h5></em>

| ![2015_median](https://github.com/refiaa/GPvMSM_Beta/assets/112306763/3901134f-3056-464f-a59c-0fc52cfdfd2d) | ![2016_median](https://github.com/refiaa/GPvMSM_Beta/assets/112306763/7fae651c-9007-4830-9c67-95b5bf2f8bef) |
|:------------------------------:|:------------------------------:|
| ![2017_median](https://github.com/refiaa/GPvMSM_Beta/assets/112306763/1908d9d6-b6af-4960-aba8-45785065f314) | ![2018_median](https://github.com/refiaa/GPvMSM_Beta/assets/112306763/ffcbbde1-1a22-49d6-90b9-94d9171cbf02) |

## 変更ログ

### 20231213
・ファイルのdir構造が変更されました。

・centerを追加しました。

・class DataDownscalerを一部変更しました（＊修正中）

### 20231220
・downscaleの正常動作を確認

・getYearSum Classを追加

・getYearSumの追加により、downscaleは一年合計データに対して実行されます。

・出力ncファイルに変数 max_value を追加 (降水量配列の最大値)

### 20231221
・GPvMSM_vsl_v.0.0.1の実行の結果に variable nameが目盛りに表示されるように変更

・GPvMSM.pyの実行の際、ディレクトリを生成できるように変更

・.envの設定を一部変更

・config.pyを一部変更

・.env、config.py、GPvMSM.pyの一部の環境変数名を修正

・requirements.txtを追加

### 20231222
・class DataDownscalerの関数の配列の次元入力問題を修正

##



