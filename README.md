# Macau 3D Model

本專案的 Unreal 資產製作規範集中於以下文件：

- [Nanite、LOD 與碰撞製作規範](docs/unreal-asset-guidelines.md)
# Macau 3D material contract

本 repository 用於以 Blender 製作、並向 Unreal Engine 交付澳門街區資產。所有模型均以真實世界的米制尺寸製作；詳細工作規則見 [`blender/README.md`](blender/README.md)。

## 目錄

```text
blender/
  startup.py                  # 建立標準 Blender 啟動檔
  scenes/                     # 街區組裝、燈光及展示場景
  assets/
    architecture/            # 建築與模組化立面
    street/                  # 道路及城市設施
    props/                   # 冷氣機、招牌、欄杆等小型資產
textures/
  source/                    # 原始及高品質工作貼圖
  export/                    # 供 Unreal 使用的最終貼圖
exports/
  fbx/                       # FBX 模型
  collision/                 # 獨立碰撞模型
references/                  # 相片、量度資料及底圖
unreal/                      # Unreal 導入規格、設定記錄及專案內容
```

空目錄以 `.gitkeep` 納入版本控制；放入正式檔案後可移除相應的 `.gitkeep`。

## 建立 Blender 啟動檔

在 repository 根目錄執行：

```bash
blender --background --factory-startup --python blender/startup.py
```

指令會建立 `blender/scenes/Macau_Startup.blend`。請以此檔案作為新場景起點，另存場景或資產檔；不要直接把所有製作內容累積在範本內。
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
# 八達新邨三維城市場景製作規格

## 1. 專案說明

本專案以澳門八達新邨為視覺中心，建立可供城市展示、建築環境預覽、鏡頭漫遊及後續即時應用整合的三維場景。場景重點是從慕拉士馬路一帶觀看時，準確呈現八達新邨的沿街特徵、周邊道路關係與城市天際線，而非製作室內空間或測繪級數碼分身。

### 目標平台與最終交付

目前尚未指定最終執行平台，因此採用以下暫定流程：

- **母檔：** Blender `.blend`，保留可編輯模型、修改器、材質、燈光、相機及 LOD 集合。
- **主要交換／即時輸出：** glTF 2.0（優先使用單一 `.glb`，亦可按整合需要交付 `.gltf`、`.bin` 與貼圖）。
- **相容輸出：** FBX（`.fbx`），供不支援 glTF 的 DCC 或引擎使用。
- **暫定平台基準：** 桌面級即時渲染及現代網頁 3D 檢視器；確定目標裝置後，須重新檢視效能預算、貼圖壓縮與材質功能。

除非交付要求另有說明，最終套件包含 `.blend` 母檔、`.glb`、`.fbx`、外部貼圖、輸出紀錄及資產清單。glTF 2.0 為材質與即時呈現的驗收基準；FBX 主要用於幾何、階層及基本材質交換，不保證與 Blender 節點材質完全一致。

## 2. 場景範圍

所有物件必須歸入以下其中一層範圍；範圍以主要相機可見度和辨識需求判定，而非只以固定半徑判定。

### 2.1 Hero Area（主體近景）

以八達新邨及慕拉士馬路近景為主，包括：

- 大廈沿街立面、主要入口與可見側立面；
- 地面商舖、櫥窗、門窗、招牌、捲閘及店面分隔；
- 冷氣機、雨篷、管線等具辨識度的附屬構件；
- 外牆污漬、褪色、修補、鏽蝕等老化特徵；
- 行人路、路緣、出入口接駁位，以及慕拉士馬路鏡頭近景。

近景應支援行人視點與沿街鏡頭，輪廓、比例、開口位置及主要招牌均須以參考資料核對。

### 2.2 Context Area（城市中景）

包括與主體相鄰、在鏡頭中可清楚辨認的環境：

- 相鄰建築的主要立面節奏與地面層界面；
- 道路交界、行車線、轉角、行人過路處與路緣關係；
- 欄杆、路牌、交通標誌、燈柱、訊號燈及其他顯眼城市設施；
- 可辨認的店面開間、招牌色塊、雨篷與重複構件。

中景以道路配置正確、街道節奏可信為優先；小型五金、細微污損及不可辨認文字可合併或省略。

### 2.3 Skyline Area（天際線遠景）

包括只用於建立城市背景和視差的遠景建築。僅需維持：

- 從主要鏡頭所見的外輪廓；
- 相對高度、退距及建築群前後關係；
- 外牆主要色塊及少量大型明暗分區；
- 對天際線有影響的屋頂量體。

遠景不得製作獨立門窗、室外機或小型屋頂設備；此類特徵應以材質色塊、低成本法線或直接省略處理。

## 3. 尺度、座標與標高

### 3.1 單位與比例

- 全案採用**真實公制單位**，`1 Blender Unit = 1 metre`。
- 建模、位移及標高均以米記錄；施工級小尺寸可在名稱或說明中以毫米標註，但進入場景前須換算為米。
- 匯入參考資料時不得以視覺猜測任意縮放；至少使用一項可靠的道路寬度、樓層高度或現場量測尺寸校準。
- 套用非必要縮放後，交付網格的物件 Scale 應為 `(1, 1, 1)`；不可用未套用縮放掩蓋錯誤尺寸。

### 3.2 原點、軸向與地理錨點

- 場景原點 `(0, 0, 0)` 定於**八達新邨面向慕拉士馬路之主要入口中心，在行人路完成面上的垂直投影點**。
- 採用右手座標概念：`+X = 東`、`+Y = 北`、`+Z = 上`；Blender 場景的北向固定為 `+Y`。
- 名為 `REF_ORIGIN` 的 Empty 放置於原點；名為 `REF_NORTH` 的 Empty／箭頭沿 `+Y` 指向真北。兩者均不可用於藝術性調位。
- 取得可靠測繪資料後，須在場景自訂屬性或隨附紀錄中補上原點的緯度、經度、採用的座標參考系統及資料來源；在此之前不得宣稱模型具有測繪精度。
- 為避免大型座標造成浮點誤差，幾何維持上述本地座標；地理座標只作錨點 metadata，不直接作模型頂點座標。

### 3.3 道路標高

- 原點所在的行人路完成面定為本地標高 `Z = 0.000 m`，作全案暫定垂直基準。
- 慕拉士馬路及相連道路須以實測、測繪或可信地形資料建立相對坡度；不得把所有路面強制壓平。
- 道路標高以行車路面中心線為主要控制線，路口、路緣頂、行人路完成面及入口門檻另設控制點；控制點高度均相對 `Z = 0.000 m` 記錄。
- 未取得標高資料前，可用 `Z = 0.000 m` 作佔位，但相關物件及紀錄必須標示 `UNVERIFIED`，不得進入最終驗收版本。

## 4. 命名與場景組織

物件與資產採用 ASCII 名稱，格式如下：

```text
<AREA>_<TYPE>_<ASSET>_<DETAIL>_<LOD>
```

- `AREA`：`HERO`、`CTX`、`SKY` 或 `REF`。
- `TYPE`：`BLD`（建築）、`ROAD`、`PROP`、`VEG`、`DECAL`、`COL`（碰撞）、`CAM`、`LGT`。
- `ASSET`：簡短而唯一的英文／拼音識別，不使用空格。
- `DETAIL`：可選的部位、序號或方位，如 `FacadeN`、`Shop_01`。
- `LOD`：`LOD0`、`LOD1`、`LOD2`；不適用 LOD 的參考物件可省略。

例：`HERO_BLD_BatTat_FacadeS_LOD0`、`CTX_PROP_LampPost_03_LOD1`、`SKY_BLD_BlockA_LOD2`。

Blender Collection 固定分為 `00_REF`、`10_HERO`、`20_CONTEXT`、`30_SKYLINE`、`40_LIGHTS_CAMERAS` 及 `90_EXPORT`。材質命名使用 `MAT_<Asset>_<Surface>`，貼圖命名使用 `T_<Asset>_<Surface>_<Map>_<Resolution>`；`Map` 可為 `BC`、`N`、`ORM`、`E` 或 `A`。同一資產的重複構件應使用 instance，避免不必要的網格及材質複製。

## 5. 品質層級與驗收重點

| 層級 | 適用範圍 | 必須呈現 | 可簡化項目 |
| --- | --- | --- | --- |
| 近景品質 | Hero Area | 可辨認門窗、入口、招牌、冷氣機、雨篷、店面分隔及外牆老化；輪廓與開口位置準確 | 不影響剪影的微小五金、不可見背面、材質中的微細凹凸 |
| 中景品質 | Context Area | 正確道路配置、路口、欄杆、路牌、燈柱及店面節奏；相鄰建築層數與主要色彩可信 | 小型管線、精細招牌文字、室內陳設、細微外牆損耗 |
| 遠景品質 | Skyline Area | 建築量體、主要色塊、相對高度及天際線關係 | 獨立門窗、招牌文字、室外機、小型屋頂設備及背光面細節 |

品質評估以指定主要相機及行人高度檢視為準。任何會明顯改變剪影、道路拓撲或八達新邨辨識度的內容，不得單純為達到效能預算而刪除；應優先以烘焙、實例化、材質合併或 LOD 解決。

## 6. 效能及資產預算

以下為未指定平台時的**暫定上限**，統計以單一完整場景、三角面（triangles）及主要相機最壞可見畫面為準。製作過程須在輸出紀錄中附上實際統計；確定平台後可經效能測試調整。

### 6.1 幾何、材質與貼圖預算

| 範圍 | LOD0 三角面上限 | 唯一材質槽上限 | 單張貼圖上限 | 建議貼圖策略 |
| --- | ---: | ---: | ---: | --- |
| Hero Area | 600,000 | 48 | 4K（4096²） | 主立面可用 2K–4K；小型道具 1K–2K；共用 ORM |
| Context Area | 250,000 | 24 | 2K（2048²） | 以 atlas、tileable 材質及重複店面模組為主 |
| Skyline Area | 50,000 | 8 | 1K（1024²） | 共用 atlas 或頂點色；避免獨立高解析貼圖 |
| **全場景上限** | **900,000** | **80** | — | 重複材質只計一次，材質槽仍須按實際 draw call 檢查 |

附加限制：

- 單一 Hero 資產原則上不超過 4 張 4K 貼圖；只有經批准的獨特主立面可例外。
- 遮罩優先打包為 ORM（Occlusion、Roughness、Metallic）；可共用 UV 的灰階資料不得各自佔用 RGB 貼圖。
- 貼圖尺寸使用 2 的冪次；不得以 4K 空白畫布承載低密度小圖。
- glTF 輸出預設使用 PNG／JPEG 相容貼圖；若目標檢視器確認支援，可另交 KTX2 壓縮版本。FBX 套件須附可重新連結的外部貼圖。

### 6.2 Draw call 預算

- 主要相機最壞畫面：**不超過 180 draw calls**。
- Hero Area 同屏：最多 100；Context Area 同屏：最多 55；Skyline Area 同屏：最多 25。
- 透明材質、雙面材質及每個材質槽均可能增加 draw call，須按目標引擎的實際 profiler 驗證，不能只以 Blender 材質數推算。
- 合併時須保留合理的剔除粒度；不得為減少 draw call 把全城合為單一不可剔除網格。

### 6.3 LOD 預算與切換

| LOD | 相對三角面目標 | 暫定切換距離（距主要相機） | 內容要求 |
| --- | ---: | ---: | --- |
| LOD0 | 100% | Hero 0–40 m；Context 0–80 m | 符合所屬範圍最高品質；Hero 保留剪影及辨識細節 |
| LOD1 | LOD0 的 40% 或以下 | Hero 40–100 m；Context 80–180 m | 合併小構件、簡化背面與曲面，保留主要開口及輪廓 |
| LOD2 | LOD0 的 10% 或以下 | Hero 100 m 以上；Context 180 m 以上；Skyline 預設 | 僅保留主量體、剪影與大型色塊，可用烘焙細節 |

- 每個可見 Hero 建築至少提供 `LOD0`、`LOD1`、`LOD2`；重複城市設施至少提供 `LOD0` 與 `LOD1`。
- Skyline Area 可直接以 `LOD2` 製作，不要求額外高精版本。
- 切換距離是暫定值；整合平台應使用螢幕覆蓋率、效能測試或引擎 LOD 規則微調，並避免明顯跳變。
- 碰撞網格獨立命名為 `COL`，不得直接以 Hero LOD0 作即時碰撞。

## 7. 輸出與驗收清單

每次候選交付須完成以下檢查：

1. 確認尺寸為米、關鍵實物抽測尺寸合理，且交付網格沒有非預期的未套用縮放。
2. 確認 `REF_ORIGIN`、`REF_NORTH`、北向及 `Z = 0.000 m` 道路標高基準沒有偏移。
3. 確認所有可見資產已歸入 Hero、Context 或 Skyline，並符合相應品質層級。
4. 檢查法線、重疊面、破面、遺失貼圖、透明排序及材質色彩空間。
5. 逐一核對三角面、唯一材質／材質槽、貼圖尺寸、draw call 與各級 LOD；超出預算須附原因及批准紀錄。
6. 從指定主要相機及行人視點檢查招牌方向、街道配置、天際線與 LOD 跳變。
7. 重新開啟 `.blend`，並在獨立檢視器測試 `.glb`；另將 `.fbx` 回匯以核對尺度、軸向、階層與基本材質連結。
8. 交付資產清單與輸出紀錄，列明 Blender 版本、輸出日期、glTF／FBX 設定、預算統計、未驗證資料及已知差異。

若平台、鏡頭路線或測繪資料其後確定，本文件中的暫定效能數字、LOD 距離與標高佔位必須在正式製作前更新並重新確認。
# Macau streetscape asset kit

This repository contains a lightweight, modular streetscape kit for building
Macau road scenes.  The geometry is stored as Wavefront OBJ so it can be used
directly in Blender, Godot, Unity, Unreal, or a GIS/DCC pipeline without a
proprietary dependency.

## Contents

- `assets/environment/` — pavement, curb, drain, asphalt, manhole, and road
  marking modules.
- `assets/street_furniture/` — Macau-oriented lights, signals, signs, railings,
  utilities, bus-stop, and parking objects.
- `assets/urban_details/` — pipes, cables, condensate drains, CCTV, drying
  racks, security grilles, lightboxes, and small storefront equipment.
- `assets/mobility/` — left-hand-traffic vehicles and compact pedestrian
  silhouettes.
- `scenes/macau_street_layout.json` — explicit, deterministic placement data.
- `tools/generate_assets.py` — dependency-free source generator for every OBJ.

All dimensions and transforms are in metres.  Object forward is local **+Y**,
up is **+Z**, and rotations use degrees in XYZ order.  The sample street uses
left-hand traffic.  Pedestrians and vehicles are kept outside the four
documented building-inspection view corridors.

## Regenerate and validate

```bash
python3 tools/generate_assets.py
python3 tools/validate_scene.py
```

The layout deliberately contains no random placement. Each instance has a
stable ID, exact transform, curb offset, and placement note so transforms can
be replaced one-by-one with photo-survey measurements when reference images or
survey control points are available.
