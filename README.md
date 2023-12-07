# GPvMSM-気象庁数値予報データ AutoDownloader - Upscailer

http://database.rish.kyoto-u.ac.jp/arch/jmadata/

気象庁の数値予報データGPVのダウンロード・アップスケーリングを自動化したコードです。

GPvMSM以外のnetCDFファイルではまだ行っていませんが、対応できると思います。

.envファイルの環境変数を変更し、GPvMSM.pyを実行することで、１時間単位の降水量データのGPvMSMが、mm/dayの一年データに変換されます。

単純合計したデータはYYYY.ncとして保存されます。

アップスケーリングを行い、Grid Sizeが変更されたデータはYYYY_2015_upscaled.ncとして保存されます。（どっちも出力名は変更可能・.envの環境変数を変更してください。）

