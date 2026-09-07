# 材質與 UV 製作管線

本文件定義澳門 3D 模型由 Blender 輸出至 Unreal Engine（UE）的材質、貼圖與 UV 標準。除非資產規格另有註明，所有 Static Mesh 均須遵守本文件；偏離標準的資產必須在交付紀錄中說明原因。

## 1. UV 標準

### 1.1 主要材質 UV（UV0）

- 每個 Static Mesh 必須提供一組主要材質 UV，並在 UE 中設為 UV Channel 0。
- UV island 不得重疊、鏡像、反轉或超出 `0–1` 空間；這項要求也適用於重複 tiling 資產。
- 可重複材質仍應保留比例一致、方向合理的 UV，並透過 Unreal 材質的 `UV_Scale` 控制 tiling，不得以重疊或超出 `0–1` 的 UV 達成。
- 展開前應套用物件 scale，並以 checker texture 檢查拉伸、接縫與 texel density。
- 接縫應放在轉角、遮蔽處或材質自然分界，避免穿過招牌、立面裝飾及其他視覺焦點。

### 1.2 Lightmap UV（UV1）

資產需要烘焙光照，或需要保留與靜態／混合光照工作流的兼容性時，必須提供獨立的 lightmap UV，並在 UE 中設為 UV Channel 1：

- 所有 island 必須位於單一 `0–1` 空間內，且不得重疊、鏡像或跨越邊界。
- island 之間以及 island 與 UV 邊界之間必須保留 padding；padding 應按目標 lightmap resolution 計算，而非只看 Blender UV 編輯器中的相對距離。
- 最低 padding 為 **4 texels**；建議使用 **8 texels**，以承受 mipmap 與降解析度。換算式為 `UV padding = padding texels / lightmap resolution`。
- 例：在 256 px lightmap 使用 4 texels padding，UV 間距至少為 `4 / 256 = 0.015625`。
- 避免過細長或不必要地碎裂的 island；保持足夠利用率，並優先把面積分配給玩家可見表面。
- UE 匯入後必須確認 `Lightmap Coordinate Index = 1`，並以目標 lightmap resolution 執行重疊與漏光檢查。

> 動態光照專案可不實際使用 UV1，但需要跨專案重用或保留烘焙光照兼容性的資產仍應製作 UV1。

## 2. Texel density

Texel density 以「每米像素數（px/m）」計算，所有數值均以貼圖最高 mip、未乘材質 UV scale 的狀態為準。資產先按用途分類，再依下表統一密度：

| 層級 | 適用範圍 | 目標密度 | 容許範圍 |
| --- | --- | ---: | ---: |
| Hero | 玩家可近距離觀察的地標、主要入口、招牌及重點建築 | 512 px/m | 410–614 px/m（±20%） |
| Context | 一般街道建築、常見外牆與中距離環境 | 256 px/m | 205–307 px/m（±20%） |
| Skyline | 遠景樓宇、天際線及通常無法接近的資產 | 128 px/m | 102–154 px/m（±20%） |

執行要求：

1. 在 Blender 套用 transform 後，以相同尺寸 checker texture 檢查密度。
2. 相鄰且觀看距離相若的表面，密度差不得超過一個層級；若 Hero 與 Skyline 資產相鄰，應把交界面調整至 Context，或以 trim sheet／detail texture 補足觀感。
3. 密度是表面解析度標準，不代表每件資產都需要獨立大貼圖；可使用 trim sheet、atlas、tileable texture 或 detail normal 達標。
4. 招牌文字、門面等局部可提高密度，但須用獨立材質槽、decal 或局部 atlas，避免無理由提高整棟建築的貼圖尺寸。
5. LOD 應維持相同 UV 比例，讓 mip 過渡時不出現材質大小跳變。

## 3. Blender 可遷移材質範圍

Blender 材質只可把下列 PBR 輸入視為能直接轉換至 UE 的內容：

- Base Color
- Roughness
- Metallic
- Normal（以 tangent-space normal map 交付）
- Ambient Occlusion（AO）
- Emissive
- 可選的 Opacity Mask

原則上每個輸入應由常數、貼圖或兩者的簡單乘算驅動。Base Color、Emissive 與 Opacity Mask 按用途採用相應色彩空間；資料貼圖一律不得以色彩貼圖解讀。

### 3.1 不可直接遷移的節點

Blender 的 Noise、Geometry、Color Ramp，以及複雜程序節點網絡，不得被視為可由匯出器直接遷移。需要保留的效果必須選擇下列其中一種方式：

1. **烘焙成貼圖**：在 Blender 將結果烘焙為 Base Color、Normal、Emissive 或 ORM 等標準貼圖，並依本文件的命名及色彩空間規則匯入 UE。
2. **在 UE 重建**：記錄所有可調參數、數學關係、座標來源、比例、seed、顏色值與參考截圖，再以 Unreal Master Material 的參數和 Material Function 重建。

程序效果的交付紀錄必須寫明採用哪一種方式。不得只交付 Blender 節點圖而沒有已烘焙貼圖或 UE 重建規格。

### 3.2 貼圖匯入設定

| 貼圖 | UE sRGB | 壓縮／注意事項 |
| --- | --- | --- |
| `_BC` Base Color | 開 | 一般色彩貼圖 |
| `_N` Normal | 關 | Normal Map compression；使用 tangent-space normal |
| `_ORM` AO/Roughness/Metallic | 關 | Masks compression；不得啟用 sRGB |
| `_E` Emissive | 開 | HDR 發光需要時使用合適格式 |
| `_M` Opacity Mask | 關 | Masks／Grayscale；只供 Masked blend mode 使用 |

## 4. ORM 通道標準

AO、Roughness、Metallic 必須打包到單一 `_ORM` 貼圖，通道順序固定如下：

| 通道 | 內容 | 值域語意 |
| --- | --- | --- |
| **R** | **Ambient Occlusion** | `0` = 完全遮蔽，`1` = 無遮蔽 |
| **G** | **Roughness** | `0` = 光滑，`1` = 粗糙 |
| **B** | **Metallic** | `0` = 非金屬，`1` = 金屬 |

命名格式為 `<Asset>_<Material>_ORM`，例如 `Bldg_A_Facade_ORM`.png。缺少某個輸入時仍要填入中性值：AO 使用 `1`、Roughness 使用該材質核准的常數、Metallic 對非金屬使用 `0`。Alpha 通道預設不使用，避免為空 Alpha 增加記憶體；如需另作用途，必須由技術美術核准並記錄。

## 5. Unreal Master Material 規格

共同基底命名為 `M_Master_Surface`，材質實例使用 `MI_<Asset>_<Surface>`。外牆、玻璃、金屬、瀝青及行人路可共用 Material Functions，但應提供用途清楚的預設 Master Material 或受控實例：

- `M_Master_Facade`
- `M_Master_Glass`
- `M_Master_Metal`
- `M_Master_Asphalt`
- `M_Master_Sidewalk`

### 5.1 所有表面材質的共同參數

| 功能 | 建議參數 | 規格 |
| --- | --- | --- |
| Tiling / UV scale | `UV_Scale` (Vector2)、`UV_Rotation` | 預設使用 UV0；所有成組貼圖共用相同 transform |
| Base Color tint | `BaseColor_Tint` (Vector3) | 與 Base Color 貼圖相乘；預設 `(1,1,1)` |
| Roughness 調整 | `Roughness_Multiplier`、`Roughness_Bias` | 先乘後加，最後 clamp 到 `0–1` |
| Normal 強度 | `Normal_Strength` | 以正確的 tangent-space normal 強度函式處理；預設 `1` |
| ORM | `Texture_ORM` | R/G/B 分別連接 AO/Roughness/Metallic |
| 世界座標污漬 | `Dirt_Enable`、`Dirt_WorldScale`、`Dirt_Amount`、`Dirt_Tint` | 使用 world-aligned mask，不依賴物件 UV 比例 |
| 頂點色混合 | `VertexBlend_Enable`、`VertexBlend_Amount` | 預設以 Vertex Color R 作混合遮罩；與污漬功能可分開開關 |
| 局部濕潤度 | `Wetness`、`Wetness_Mask`、`Wet_Roughness`、`Wet_Darken` | 遮罩範圍內降低 roughness 並輕微壓暗 Base Color，不應把非金屬變為金屬 |
| Emissive | `Emissive_Texture`、`Emissive_Tint`、`Emissive_Intensity` | 支援招牌；強度以 Scalar 控制，預設 `0` |
| Macro variation | `Macro_Texture`、`Macro_Scale`、`Macro_Amount` | 大尺度、低頻變化，用於打散重複感 |
| Micro variation | `Micro_Normal`、`Micro_Scale`、`Micro_NormalStrength` | 只在近景啟用；配合距離淡出，避免遠距閃爍 |

可選功能必須由 Static Switch 控制，以免未使用的污漬、頂點混合、濕潤、Emissive 或 variation 分支持續產生 shader 成本。材質實例不得改變 `_ORM` 通道解讀順序。

### 5.2 各材質用途要求

#### 外牆（Facade）

- 預設 Opaque；支援 tileable 基底、trim sheet 或 atlas。
- 必須支援世界座標污漬或 Vertex Color R 混合，用於牆腳、冷氣機下方及老化區域。
- Hero 外牆啟用 macro color variation 與可距離淡出的 micro normal；Context 視效能選用；Skyline 預設關閉 micro variation。
- 招牌應使用獨立 mask／材質槽或 decal 驅動 Emissive，不應讓整個外牆材質發光。

#### 玻璃（Glass）

- 依平台與效能預算選用 Opaque fake glass、Masked 或 Translucent 版本；預設優先使用成本較低的 Opaque／Masked 方案。
- 提供 `Glass_Tint`、`Glass_Roughness`、`Reflection_Strength`、`InteriorCubemap`（如採用）及污漬／雨痕遮罩。
- Metallic 固定為 `0`；不得以 Metallic 模擬反射玻璃。Opacity Mask 只在 Masked 版本啟用。
- 窗框金屬應使用獨立材質區域或金屬實例，不與玻璃的 shading model 混用。

#### 金屬（Metal）

- 裸露金屬區 Metallic 應接近 `1`；油漆、鏽蝕及污垢覆蓋區按物理材質以 mask 混合至非金屬值。
- 支援 brushed direction、細節 normal 及 roughness variation；方向性效果須與 UV 或明確的 object/world axis 對齊。
- 濕潤功能只調整表面顏色及 roughness，不覆寫金屬／非金屬分類。

#### 瀝青（Asphalt）

- 使用 world-aligned 或統一 UV 尺度，確保道路模組接縫兩側顆粒大小一致。
- 支援 macro variation、micro aggregate normal、積水／濕潤遮罩與 Vertex Color R 局部混合。
- Metallic 固定為 `0`；標線宜用 decal、獨立 mask 或材質層，不直接畫入所有重複路面。
- Micro normal 必須隨距離淡出，以降低摩爾紋與閃爍。

#### 行人路（Sidewalk）

- 支援磚塊／石板 tiling、接縫 normal、macro 色差及 Vertex Color R 污漬混合。
- 世界尺度應與相鄰模組一致，並保持鋪面圖案方向連續。
- 濕潤遮罩可由 Vertex Color G 或獨立 mask 驅動，避免與預設 Dirt 的 Vertex Color R 衝突。
- Metallic 預設為 `0`；只有實際金屬嵌件才以獨立 mask 或材質處理。

## 6. 命名與交付

| 類型 | 格式 | 範例 |
| --- | --- | --- |
| Static Mesh | `SM_<Area>_<Asset>` | `SM_Cotai_HotelA` |
| Master Material | `M_Master_<Type>` | `M_Master_Facade` |
| Material Instance | `MI_<Asset>_<Surface>` | `MI_HotelA_Facade` |
| Base Color | `<Asset>_<Material>_BC` | `HotelA_Facade_BC` |
| Normal | `<Asset>_<Material>_N` | `HotelA_Facade_N` |
| ORM | `<Asset>_<Material>_ORM` | `HotelA_Facade_ORM` |
| Emissive | `<Asset>_<Material>_E` | `HotelA_Sign_E` |
| Opacity Mask | `<Asset>_<Material>_M` | `HotelA_Fence_M` |

每項交付需包含來源 `.blend`、匯出 mesh、使用中的貼圖、材質實例參數，以及任何程序效果的烘焙或 UE 重建說明。貼圖解析度應按 texel density 和實際表面尺寸選擇，不可單純把所有資產設為相同解析度。

## 7. 驗收清單

- [ ] 每個 Static Mesh 的 UV0 均位於 `0–1`，並符合不重疊、不鏡像及不反轉的主要材質 UV 要求。
- [ ] 需要烘焙光照或兼容性的資產具備不重疊 UV1、足夠 padding，且 `Lightmap Coordinate Index` 正確。
- [ ] Hero、Context、Skyline 的 texel density 符合表列目標，相鄰表面沒有突兀解析度差異。
- [ ] 材質只依賴可遷移 PBR 輸入；Blender 程序節點已烘焙或附有 UE 重建紀錄。
- [ ] `_ORM` 的 **R = AO、G = Roughness、B = Metallic**，且 sRGB 已關閉。
- [ ] Normal 貼圖匯入為 Normal Map，資料貼圖使用正確壓縮與色彩空間。
- [ ] 材質實例的 tiling、tint、roughness、normal、污漬／頂點混合、濕潤、Emissive 及 variation 功能按資產層級設定。
- [ ] 未使用的可選功能已由 Static Switch 關閉，並完成近、中、遠距離視覺與效能檢查。
