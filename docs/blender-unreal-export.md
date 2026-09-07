# Blender → Unreal 靜態資產導入基準

本文件是 Macau 3D model 的單一 FBX 基準。後續靜態資產必須沿用
`Macau Unreal Selected` preset；任何偏差都要在資產導入紀錄中註明原因。

> **目前狀態（2026-09-07）**：倉庫尚未包含 Blender/FBX 資產、貼圖或 Unreal
> 專案，因此未能在本環境實際匯出、導入或截圖。下列五個固定測試 ID、設定和驗收表
> 已建立；在有源資產及 Unreal 專案的工作站完成「實測紀錄」前，不可把基準標記為已驗證。

## 1. 固定的五種代表性測試資產

不要以五個最簡單的模型取代這組樣本。每一列選擇專案內幾何／材質最具代表性的實物，
並把實際檔名和 Unreal Content Browser 路徑填入表格。

| 測試 ID | 類型 | 選取條件 | 源資產 / UE 路徑 | 狀態 |
|---|---|---|---|---|
| `T01_FacadeModule` | 一個建築立面模組 | 至少兩個材質槽、硬邊、UV0/UV1 | 待指定 | ⬜ 待測 |
| `T02_BuildingSection` | 一個完整建築區段 | 多物件、可重複模組及 Nanite 候選 | 待指定 | ⬜ 待測 |
| `T03_StreetProp` | 一個冷氣機或燈柱 | 選較常重複的一款，測 instance | 待指定 | ⬜ 待測 |
| `T04_RoadSidewalk` | 一段道路及行人路 | UV 尺度、路緣硬邊及多材質 | 待指定 | ⬜ 待測 |
| `T05_CustomCollision` | 一個入口或欄杆 | 必須帶一個或多個 `UCX_` 碰撞 mesh | 待指定 | ⬜ 待測 |

每個匯出測試另加入一個只供量度的 `SM_TestDoor_200cm`：Blender Dimensions 的
Z 必須是 **2.000 m**，Apply Scale 後 Scale 必須是 `(1, 1, 1)`。導入 Unreal 後以
Modeling Mode/測量工具或 Static Mesh bounds 讀取，其高度驗收值是 **200 uu**（允差
±0.1 uu），不能靠修改 Import Uniform Scale 達成。

## 2. Blender 源檔規則

### 場景與物件

1. `Scene Properties > Units` 設 `Metric`、`Unit Scale = 1.0`、Length `Meters`。
2. 世界座標 **Z 向上**；模型正面統一面向 **-Y**。物件原點是 Unreal pivot：建築模組
   通常放在首層地面角點，道路放在拼接角點，道具放在落地中心。需要額外 socket 時用
   Empty，名稱以 `SOCKET_` 開頭。
3. 對可見 mesh 和碰撞 mesh 執行 `Ctrl+A > Rotation & Scale`；導出前 Rotation 應為
   `(0, 0, 0)`、Scale 應為 `(1, 1, 1)`。不要 Apply Location，否則會破壞約定的 pivot。
4. 確認面朝外，設定硬／軟邊並保留 Custom Split Normals。每個 mesh 至少有 `UVMap`
   （UV0）；需要 baked/static lighting 時另有不重疊、位於 0–1 的 `LightmapUV`（UV1）。
5. 材質槽依最終 index 排序，空槽也要在導出前移除；名稱不使用 `.001` 等臨時尾碼。
6. 在 modifier stack 最後加入 **Triangulate**（Keep Normals），讓 Blender 與 Unreal 使用
   相同三角形，尤其是有 normal map 的資產。

### 自訂碰撞

* 碰撞物件與 render mesh 在同一次 FBX 選取並輸出，命名為
  `UCX_<RenderMeshName>_00`、`UCX_<RenderMeshName>_01`……。
* 每個 `UCX_` 部件必須是封閉、凸形、不互相穿插的低面數 mesh；凹形入口拆成數個凸體。
* 碰撞 mesh 不設材質、不與 render mesh 合併，也不可另作 FBX。若採簡單盒／球碰撞，
  分別使用 Unreal 支援的 `UBX_` / `USP_` 名稱。

## 3. 安裝及使用 FBX preset

Preset 檔位於：

```text
tools/blender/presets/operator/export_scene.fbx/macau_unreal_selected.py
```

在 Blender 執行 `Edit > Preferences > File Paths > Script Directories` 所指的使用者 scripts
目錄，將檔案複製到相同的 `presets/operator/export_scene.fbx/` 子目錄，重啟 Blender。
然後：

1. 在 Outliner 只選可見 mesh、所需 `EMPTY/SOCKET_` 及相應碰撞 mesh；不要選 collection
   instance 本身。
2. 執行 `File > Export > FBX (.fbx)`，從 Operator Presets 選
   **Macau Unreal Selected**。
3. 確認右側摘要符合下表，輸出到每個測試 ID 的獨立 FBX。不要臨時覆寫 preset。

| FBX 選項 | 固定值 | 用意 |
|---|---:|---|
| Selected Objects | On | 排除未選物件與組織用 collection |
| Object Types | Mesh, Empty | 硬性排除 Camera、Light |
| Scale / Apply Unit | 1.0 / On | 寫入一致的單位轉換 |
| Apply Scalings | FBX All (`FBX_SCALE_NONE`) | 不額外烘焙倍數 |
| Forward / Up | `-Y` / `Z` | 對應專案座標基準 |
| Apply Transform | Off | 避免實驗性的額外旋轉烘焙 |
| Apply Modifiers | On | 輸出已核准的最終幾何 |
| Smoothing | Normals Only | 保留 custom split normals |
| Tangent Space | On | 輸出 tangent/binormal；mesh 必須有 UV |
| Triangulate Faces | Off | 使用源檔 Triangulate modifier 的固定結果 |
| Add Leaf Bones / Bake Animation | Off / Off | 靜態資產不輸出骨架或動畫 |
| Path Mode / Embed Textures | Auto / Off | 保留材質槽但不封裝貼圖 |

FBX 不會把 Blender collection 當作獨立幾何輸出；真正的保護措施是 `Selected Objects` 加上
物件類型白名單。導出前仍要在 Outliner 人工檢查 selection。

## 4. Unreal 統一導入設定

在 Content Browser 的測試資料夾用 **Import**（不是把五種資產 Combine 成單一 mesh）：

| Unreal FBX Import 選項 | 固定值 / 規則 |
|---|---|
| Mesh Type | Static Mesh |
| Skeletal Mesh / Import Animations | Off / Off |
| Import Mesh | On |
| Import Uniform Scale | `1.0` |
| Convert Scene | On |
| Force Front XAxis | Off |
| Convert Scene Unit | On |
| Combine Meshes | Off（只有經批准的單一組合資產才可 On） |
| Import Normals and Tangents | On；Normal Import Method 選此項 |
| Normal Generation Method | MikkTSpace（只作一致性基準，不應重算法線） |
| Import Materials / Textures | Off / Off；使用既有 Material Instance |
| Generate Lightmap UVs | Off（使用 Blender UV1）；沒有 UV1 的明確例外才 On |
| Auto Generate Collision | Off（`T05` 使用命名碰撞；其他資產另行決定） |
| One Convex Hull per UCX | Off，以保留多個已拆分的凸體 |
| Build Nanite | 依第 6 節逐資產評估，不作全域強制 |

不同 Unreal 版本的欄位名稱可能略有差異；值的意圖不得改變。Reimport 必須使用相同設定，
並在版本控制中提交 `.uasset` 及必要的材質實例，而不是提交 Derived Data Cache。

## 5. 貼圖色彩空間

FBX 只傳遞材質槽，不是貼圖色彩空間的權威。導入／指定 Texture Asset 時逐張核對：

* Base Color、Emissive、非資料型彩色 mask：**sRGB On**。
* Normal：Compression Settings = **Normalmap**、**sRGB Off**。
* Roughness、Metallic、Ambient Occlusion、Opacity mask、Height 及 packed ORM：
  **sRGB Off**；packed ORM 不可被當成彩色貼圖壓縮。
* 材質 instance 的槽位必須對應 Blender 材質槽用途；不依賴 FBX 自動生成材質。

## 6. 逐項驗收矩陣

每一格填 `PASS`、`FAIL（issue 連結）` 或 `N/A（理由）`。未填即未驗證。

| 檢查 | T01 | T02 | T03 | T04 | T05 | 驗收方法 |
|---|---|---|---|---|---|---|
| 軸向與 pivot |  |  |  |  |  | 拖入原點；正面朝專案 forward，旋轉為 0，pivot 在約定點 |
| Scale |  |  |  |  |  | `SM_TestDoor_200cm` 高 200 ±0.1 uu；資產 bounds 與 Blender 尺寸相符 |
| 法線和 tangent |  |  |  |  |  | Static Mesh normal/tangent 顯示；斜光下無接縫、翻面或陰影破裂 |
| UV 通道 |  |  |  |  |  | UV0 完整；需 lightmap 者 UV1 無重疊且 Light Map Coordinate Index = 1 |
| 材質槽順序 |  |  |  |  |  | Element index、名稱及指定面與 Blender 完全相同 |
| 貼圖色彩空間 |  |  |  |  |  | 依第 5 節核對每張 Texture Asset |
| 碰撞 |  |  |  |  |  | Show > Simple Collision；Player Collision 視圖及實際阻擋測試 |
| Nanite 相容性 |  |  |  |  |  | 開啟後無 fallback/材質警告；透明、WPO 等限制者記 N/A 理由 |
| LOD |  |  |  |  |  | Screen Size 逐級檢視，無明顯爆點；Nanite-only 者記錄 fallback 策略 |
| instance 重建 |  |  |  |  |  | 依下節重建後抽查 transform、數量、材質 override 與命名 |

Nanite 不是品質勾選框：高密度、不透明的建築與道路可作候選；簡單碰撞、材質槽、UV 和
pivot 仍須驗證。小型低面數道具或使用不支援材質功能的 mesh，保留傳統 LOD 並記錄理由。

## 7. Instance 重建規則

FBX 不作為 Blender collection instance 的權威傳輸格式。採以下固定方式重建：

1. 每個唯一 mesh 各輸出一次，以 Blender object name 作穩定資產 ID。
2. 重複數量少或需逐件互動者，在 Unreal 以多個 Static Mesh Actor 重建。
3. 大量相同且材質一致者，以 Blueprint 的 **ISM**；需要不同 LOD/cull 或密集場景者以
   **HISM**。不要為每個 instance 複製 Static Mesh asset。
4. 從 Blender 另行匯出 instance manifest（資產 ID、translation、quaternion rotation、
   scale），轉換到 Unreal 座標後由 Editor Utility/Blueprint 建立。抽查首個、末個和至少
   10% instance；負 scale 必須先消除或另建鏡像 mesh，避免 tangent/collision 反轉。

## 8. 實測紀錄（必填後才可核准）

| 欄位 | 紀錄 |
|---|---|
| Blender 版本 / commit | 待填 |
| Unreal 版本 / project commit | 待填 |
| Preset 檔 SHA-256 | 待填 |
| 測試日期、操作者、平台 | 待填 |
| 2 m 門在 UE 的實測高度 | 待填（目標 200 ±0.1 uu） |
| 五個 FBX 的檔名與 SHA-256 | 待填 |
| 驗收矩陣結果 / issue | 待填 |

每次 Blender 或 Unreal 大版本升級、FBX importer 改動、或 preset 變更，都要重跑五項測試。
將 Export 與 Import options 展開後的截圖放在 `docs/images/blender-unreal/`，在本節加入相對
連結；若因審核政策不提交圖片，則完整記錄版本、所有非預設值及產物雜湊。
