# Macau 3D model — 燈光與固定鏡頭基準

此倉庫提供可重複執行的 Blender 場景設定腳本，目的是先建立**不會掩蓋模型及材質問題**的驗收環境，再提供澳門亞熱帶日間氣氛及可選夜景。腳本不包含或臆測建築模型；所有位置均集中在設定檔，方便在模型完成定位後調整。

## 使用方法

1. 以 Blender 開啟模型檔，確認模型使用公尺、`Z` 軸向上。
2. 按項目原點編輯 `config/scene_setup.json` 的燈光及鏡頭座標；相機的 `target` 是畫面中心，而非歐拉角。
3. 在 Blender 的 **Scripting** 工作區開啟並執行：

   ```python
   exec(compile(open("/path/to/Macau-3D-model/scripts/setup_scene.py", encoding="utf-8").read(), "setup_scene.py", "exec"))
   ```

   或以命令列處理現有檔案：

   ```bash
   blender model.blend --background --python scripts/setup_scene.py -- --config config/scene_setup.json --save-as model-lit.blend
   ```

腳本可安全重跑：它只重建名稱以 `MACAU_` 開頭的燈光、世界及相機資料，不會刪除模型。首次執行使用 `neutral_overcast`，供材質驗收。

## 三套光照

| 場景 | Collection / View Layer | 用途 |
| --- | --- | --- |
| 中性陰天 | `MACAU_LIGHTING_NEUTRAL` / `LOOKDEV_NEUTRAL` | 大面積柔光、低反差但保留暗部，無夕陽色偏；固定 6500 K、AgX `Medium High Contrast`，作為材質判斷基準。 |
| 亞熱帶日間 | `MACAU_LIGHTING_SUBTROPICAL` / `DAY_SUBTROPICAL` | 較高天空反射、柔和太陽及世界體積霧，模擬高濕度的空氣透視；霧密度刻意保持低量，避免吞掉立面細節。 |
| 可選夜景 | `MACAU_LIGHTING_NIGHT` / `NIGHT_OPTIONAL` | 商舖燈箱、街燈、住宅窗光及車燈分成四個子區域；使用少量代表光源，應優先複製 emissive 幾何而非無限制增加燈。 |

每個 View Layer 僅啟用相應燈光 collection。切換 View Layer 即可比較，而不需手動隱藏燈具。夜景預設建立但不設為活動層。

## 固定攝影機

腳本建立下列 7 個鎖定攝影機；所有展示鏡頭保持 1.65–1.70 m 人眼高度及 42–50 mm 焦距，高位總覽則使用 55 mm，避免超廣角扭曲比例：

- `CAM_MURRAY_ROAD_PANORAMA`：沿慕拉士馬路的街道全景（50 mm；使用合理距離取得景寬，而非超廣角）。
- `CAM_PAT_TAT_FRONT`、`CAM_PAT_TAT_OBLIQUE`：八達新邨主立面正面及斜角。
- `CAM_SHOPS_EYE`、`CAM_ENTRANCE_EYE`：商舖與入口的人眼高度近景。
- `CAM_HIGH_RELATIONSHIP`：檢查道路與樓宇關係的高位總覽。
- `CAM_REFERENCE_MATCH_01`：主要參考相片對照鏡頭。其自訂屬性 `reference_status` 預設為 `ALIGN_REQUIRED`；取得原相片、拍攝點及 EXIF 後，必須更新位置、焦距和相機移軸，才可標記為已匹配。

相機構圖疊加顯示三分線，並將焦距、用途及驗收狀態寫入自訂屬性。請勿把任何展示鏡頭降至 35 mm 以下；若場地狹窄，應使用相機移軸或調整裁切，而不是以超廣角掩飾比例。

## 驗收流程

1. 在 `LOOKDEV_NEUTRAL` 逐一檢查材質色值、粗糙度、法線、檐底及入口暗部；不要用日間或夜景判斷基礎材質。
2. 切換 `DAY_SUBTROPICAL`，確認遠景柔化但近景輪廓清楚、天空反射不過曝。
3. 若交付需要夜景，才渲染 `NIGHT_OPTIONAL`；按 `SHOP_SIGNS`、`STREET_LAMPS`、`RESIDENTIAL_WINDOWS`、`VEHICLE_LIGHTS` 分區調光。
4. 依序檢查所有 `MACAU_CAMERAS` 相機；比對參考相片前先完成 `CAM_REFERENCE_MATCH_01` 校準。

配置檔採純 JSON，可先執行 `python3 tests/test_config.py` 檢查命名、焦距、人眼高度、夜景分組及光照數值是否符合最低規則。
