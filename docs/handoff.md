# 本機 Blender／Codex 交接記錄

更新日期：2026-09-07

## 目前狀態

- 第 1 階段已完成：五個建築模組、命名、座標、FBX 測試輸出與 PBR 契約已建立。
- 第 2 階段已完成：程序模型包括樓層窗列、露台、冷氣機、服務管、裙樓柱、商舖、簷篷、道路、路緣、排水和街燈。
- 第 3 階段進行中：Hero 立面已有獨立窗框和露台欄杆，但實景校準正等待合法參考照片與可靠尺寸。
- 所有場地尺寸仍是 `ESTIMATED_AWAITING_SURVEY`，不可視作實測值。
- 目前未提交 `.blend`、FBX 或貼圖等二進制成品；它們由本機生成或按外部資產策略保存。

## 重要檔案

| 檔案 | 用途 |
| --- | --- |
| `architecture_manifest.json` | 五個 Blender／Unreal 建築模組及輸出契約 |
| `material_manifest.json` | PBR 基礎材質、ORM 通道及建築材質槽對應 |
| `site_manifest.json` | 程序灰模尺寸、街道設施及驗收攝影機 |
| `references/calibration_manifest.json` | 參考來源、尺寸證據、可信程度與校準狀態 |
| `scripts/blender_build_blockout.py` | 建立目前完整場景的主要 Blender 入口 |
| `scripts/validate_project.py` | 不依賴 Blender 的整體合約檢查 |
| `docs/production-stages.md` | 七階段進度與完成條件 |

## 回家後首次設定

1. 安裝 Blender 4.x，安裝時啟用或記下 command-line executable 路徑。
2. Clone／pull 最新 repository，並在 repository 根目錄開啟 Codex。
3. 先確認 Python 合約，再確認 Blender：

```bash
python3 scripts/validate_project.py
blender --version
```

macOS 若 `blender` 不在 `PATH`：

```bash
/Applications/Blender.app/Contents/MacOS/Blender --version
```

Windows PowerShell 示例：

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --version
```

## 第一次 Blender runtime 驗收

先生成 `.blend`：

```bash
blender --background --python scripts/blender_build_blockout.py -- \
  --save build/PatTat_Blockout.blend
```

然後在 Blender GUI 打開 `build/PatTat_Blockout.blend`，依次檢查：

1. `EXPORT_ARCHITECTURE` 下是否只有五個預定模組 Collection；
2. 三座塔樓、裙樓、入口和十組商舖是否存在；
3. 窗框、露台、欄杆、冷氣機和管道有否重疊或浮空；
4. 道路、行人路、路緣和店面之間有否穿插；
5. `CAM_Street_Hero`、`CAM_Facade`、`CAM_Overview` 是否能正常取景；
6. 材質名稱、物件尺寸和 Metric 單位是否正確；
7. 儲存後重開檔案，確認 Collections、材質與 custom properties 沒有遺失。

若命令失敗，保留完整終端輸出，交給 Codex 修正後再生成；不要在失敗的半成品 `.blend` 上繼續大量手工修改。

## 第三階段參考資料交接

優先自行拍攝或使用明確容許衍生模型的資料。最低需要：正面、東側斜角、西側斜角和道路環境；最好另外包含入口、商舖分間、天台輪廓，以及一個可量度的門、地磚或欄杆。

把素材放在不會誤提交的受控位置，然後只把來源 metadata 寫入 `references/calibration_manifest.json`：

- 穩定且唯一的 `id`；
- 拍攝日期／希望還原的年份；
- 作者或來源機構；
- 授權或使用依據；
- repository-relative 路徑或受控外部 URI；
- 該來源支持哪些尺寸或視角。

仍為 `BLOCKOUT_ESTIMATE` 的尺寸必須保持 `LOW` confidence 且 `source_id` 為 `null`。沒有來源及尺寸交叉檢查前，不可把 `calibration_status` 改成 `CALIBRATED`。

## 建議交給本機 Codex 的第一個指令

> 讀取 `docs/handoff.md` 和 `docs/production-stages.md`，執行所有 validators 和 unit tests，再用本機 Blender 執行 `scripts/blender_build_blockout.py`。保留完整 Blender 輸出，檢查生成的 `.blend`、三個固定鏡頭和物件穿插；先修復 runtime 問題並產生驗收 render，不要把估算尺寸標記成已校準。

## 已知限制與下一步

- 先前容器沒有 Blender；所有 Blender API 程式只通過 Python 編譯及 manifest 測試，尚未在該容器執行。
- 容器的 Ubuntu repositories、OpenAI 文件和網頁搜尋均受網絡代理阻擋，因此無法在容器安裝 Blender 或核實／下載參考資料。
- 本機首次成功生成及視覺驗收後，才應處理相片匹配、準確塔樓比例、窗列、入口和商舖分間。
- 第 3 階段校準完成後才進入第 4 階段高精度街道道具；不要用更多未校準細節掩蓋主比例問題。
