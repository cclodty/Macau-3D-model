# Blender 製作規格

## 單位與座標

- Unit System：`Metric`。
- Unit Scale：`1.0`。
- Length：`Meters`；`1 Blender Unit = 1 m`。
- 世界座標 `Z` 軸向上。
- 物件局部前方向統一為 `-Y`；本 repository 輸出到 Unreal 時以 `-Y` 為 Forward、`Z` 為 Up。
- 建築資產的原點應放在地面，優先使用方便貼齊模組網格的結構角點。
- 小型道具的原點應放在底部中心；壁掛或吊掛物則放在實際安裝點。
- 所有可輸出物件在交付前必須套用 Rotation 和 Scale，使 rotation 為 `(0, 0, 0)`、scale 為 `(1, 1, 1)`。Location 是否套用則按資產樞紐及場景定位需要決定。

## 檔案與 Collections

完整街區組裝檔只能存放於 `scenes/`；可重用的獨立資產分別存放於 `assets/architecture/`、`assets/street/` 或 `assets/props/`。每個可重用資產應有自己的 `.blend` 檔，不應只存在於街區組裝檔。

啟動範本提供以下頂層 Collections：

- `00_CONTEXT`：參考底圖及不可輸出的場景脈絡。
- `10_ARCHITECTURE`：建築及模組化立面 linked collections。
- `20_STREET`：道路及城市設施 linked collections。
- `30_PROPS`：小型資產 linked collections。
- `40_LIGHTING`：燈光。
- `50_CAMERAS`：展示鏡頭。

重複物件必須透過 **Link**（`File > Link`）引用資產檔中的 collection，並以 collection instance 重用。需要在組裝檔調整 linked asset 時使用 Library Override；不要複製出失去來源關係的獨立 mesh。

## 建立範本

[`startup.py`](startup.py) 是可重現的範本來源。使用 Blender 執行：

```bash
blender --background --factory-startup --python blender/startup.py
```

腳本會清除 factory scene、設定單位、建立標準 Collections，並輸出 `scenes/Macau_Startup.blend`。若要把設定安裝成個人 Blender 的預設啟動檔，先開啟輸出的檔案，再選擇 `File > Defaults > Save Startup File`；此操作會修改個人 Blender 設定，不應由 repository 腳本自動執行。

## 交付前檢查

1. 尺寸與參考量度一致，且場景單位仍為 Metric / 1.0。
2. 原點符合資產類型，局部前方向為 `-Y`。
3. 輸出物件的 Rotation 及 Scale 已套用。
4. 重複資產仍為 linked collection instances。
5. FBX 使用 `-Y Forward`、`Z Up`，模型放入 `exports/fbx/`。
6. 必須獨立管理的碰撞模型放入 `exports/collision/`。
7. Unreal 最終貼圖只放入 `textures/export/`，原始工作檔保留在 `textures/source/`。
