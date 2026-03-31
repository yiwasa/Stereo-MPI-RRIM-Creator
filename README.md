# Stereo MPI-RRIM Creator for QGIS

English | [日本語](#japanese-日本語)

## Overview
**Stereo MPI-RRIM Creator** is a QGIS Processing Plugin that generates Morphometric Protection Index Red Relief Image Maps (MPI-RRIM) from Digital Elevation Models (DEMs). It supports not only standard 2D image generation but also various 3D stereoscopic formats (Anaglyph, Parallel-eyed, and Cross-eyed stereo pairs). 

It also includes a high-resolution processing option (3x resampling) to significantly reduce the "terracing effect" often seen in low-resolution DEMs.

## Features
* **MPI & Slope Calculation**: Calculates the Morphometric Protection Index (MPI) and Slope from a single DEM.
* **Color Modes**: Choose between "Red Relief" (Slope: Red, MPI: Cyan) and "Blue Relief" (Slope: Black, MPI: Cyan).
* **Stereoscopic Outputs**:
  * Normal (2D Image)
  * Anaglyph (for Red-Cyan glasses)
  * Stereo Pair (Parallel-eyed / 2 separate layers)
  * Stereo Pair (Cross-eyed / 2 separate layers)
* **High-Resolution Generation**: Upsamples the DEM by 3x internally before calculation to generate high-quality, smooth terrain maps.

## Installation
1. Download the repository as a ZIP file.
2. Extract the folder and place it in your QGIS plugins directory:
   * Windows: `C:\Users\User\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   * Mac: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
3. Restart QGIS, open **Manage and Install Plugins**, and enable the plugin.
4. The tool will appear in the **Processing Toolbox**.

## Parameters & Usage
* **Search Radius (pixels)**: Recommended to set the equivalent of **150 meters** in reality.
  * Example: For a 1m DEM, set to `150`. For a 5m DEM, set to `30`.
* **MPI / Slope Gamma Correction**: Adjusts the contrast. If you want to darken the valley bottoms, decrease the "MPI Gamma Correction" value.
* **Stereo Exaggeration Factor**: Controls the depth/strength of the 3D effect.
* **High-Resolution Generation**: Check this box to enable 3x resampling. It produces much better quality but increases processing time.

## References
* Kaneda, H., & Chiba, T. (2019). Stereopaired Morphometric Protection Index Red Relief Image Maps (Stereo MPI‐RRIMs): Effective Visualization of High‐Resolution Digital Elevation Models for Interpreting and Mapping Small Tectonic Geomorphic Features. *Bulletin of the Seismological Society of America*, 109(1), 99-109. [doi: 10.1785/0120180166](https://pubs.geoscienceworld.org/ssa/bssa/article-abstract/109/1/99/567965/Stereopaired-Morphometric-Protection-Index-Red?redirectedFrom=fulltext)
* [Stereo MPI-RRIMs Calculator (Chuo University)](https://civil.r.chuo-u.ac.jp/lab/geology/5_mrrim/mrrim.html)

---

# Japanese (日本語)

## 概要
**Stereo MPI-RRIM Creator** は、DEM（数値標高モデル）から「MPI-RRIM（立体視対応のMPI赤色立体地図）」を作成するQGISプロセシングプラグインです。通常の2D画像だけでなく、アナグリフ（赤青メガネ用）やステレオペア（平行法・交差法）の生成に対応しています。

また、DEM特有の「段丘効果（テラス状のギザギザ）」を低減するための**高画質生成（3倍リサンプリング）機能**を搭載しており、より滑らかで精細な地形表現が可能です。

## 主な機能
* **MPIと傾斜角の計算**: DEMからMPI（Morphometric Protection Index：保護指数）と傾斜角を計算します。
* **カラーモード**: 「赤色立体（傾斜:赤, MPI:シアン）」と「青色立体（傾斜:黒, MPI:シアン）」から選択可能。
* **ステレオ出力対応**:
  * 通常（2D画像）
  * アナグリフ（赤青メガネ用）
  * ステレオペア（平行法 / 2枚の別レイヤ出力）
  * ステレオペア（交差法 / 2枚の別レイヤ出力）
* **高画質生成オプション**: 処理前にDEMを内部で3倍に拡大（リサンプリング）してから計算を行うことで、解像度の粗いDEMでも高精細な画像を出力します。

## インストール方法
1. 本リポジトリをZIP形式でダウンロードします。
2. 解凍したフォルダをQGISのプラグインディレクトリに配置します。
   * Windows: `C:\Users\ユーザー名\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   * Mac: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
3. QGISを再起動し、「プラグインの管理とインストール」から本プラグインを有効化します。
4. **プロセシングツールボックス**内にツールが追加されます。

## 使い方・パラメータのコツ
* **探索半径（ピクセル）**: 実距離で **150m** 相当になるように設定することをおすすめします。
  * 例: 1m DEMの場合は `150`。5m DEMの場合は `30`。
* **ガンマ補正値**: コントラストを調整します。谷底をより暗く表現したい場合は、「MPIのガンマ補正値」を小さく（例：0.8など）設定してください。
* **立体視の視差係数**: ステレオ画像の立体感（奥行き）の強さを調整します。
* **高画質生成（3倍リサンプリング）**: チェックを入れると画質が向上し段丘効果が低減しますが、処理時間は長くなります。

## 参考文献
* Kaneda, H., & Chiba, T. (2019). [doi: 10.1785/0120180166](https://pubs.geoscienceworld.org/ssa/bssa/article-abstract/109/1/99/567965/Stereopaired-Morphometric-Protection-Index-Red?redirectedFrom=fulltext)
* [Stereo MPI-RRIMs Calculator (中央大学)](https://civil.r.chuo-u.ac.jp/lab/geology/5_mrrim/mrrim.html)

---
## License
[MIT License](LICENSE) (※必要に応じてライセンスを変更してください)