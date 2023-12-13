# GPvMSM-気象庁数値予報データ AutoDownloader - Upscailer

> ## class DataDownscalerの修正がまだ終わっていません、極力centerを使ってください。



http://database.rish.kyoto-u.ac.jp/arch/jmadata/

気象庁の数値予報データGPVのダウンロード・アップスケーリングを自動化したコードです。

GPvMSMや気象庁数値予報データに関するもっと詳しい情報は上記のリンクをご参照ください。

###

GPvMSM以外のnetCDFファイルではまだ行っていませんが、対応できると思います。

.envファイルの環境変数を変更し、GPvMSM.pyを実行することで、１時間単位の降水量データのGPvMSMが、mm/dayの一年データに変換されます。

単純合計したデータはYYYY.ncとして保存されます。

アップスケーリングを行い、Grid Sizeが変更されたデータはYYYY_upscaled.ncとして保存されます。（どっちも出力名は変更可能・.envの環境変数を変更してください。）


GPvMSM_vsl_v.0.0.1.pyは結果データを可視化させるためのコードですが、RAWDATAやYYYY.ncとして変換されたファイルは緯度が反転されていますので、ちゃんと表示されません。
コード内のwrap_data関数を一部修正すれば問題なく表示されます。YYYY_upscaled.ncは緯度を反転して保存したデータでGPvMSM_vsl_v.0.0.1.pyでちゃんと表示されます。

ご参照ください。

###

.envのUPSCALING_METHODは、アップスケーリングする時、格子の中の値のうち、出力データとしてなにを選定するのかの変数

maxは最大値で、格子ないの配列の中の最大値を利用・medianは中央値・空欄にすると平均値のデータが出力方法となる。

centerとは、新しく構成したGridの空間的に真ん中に位置する数値を代表値として設定する方法です。現在、Centerには問題がないように思われます。

###

### 20231213
・ファイルのdir構造が変更されました。

・centerを追加しました。

・class DataDownscalerを一部変更しました（＊修正中）

###