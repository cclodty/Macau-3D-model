# Blender 與 Unreal 資產命名規則

本文件規範 Blender 場景中的 Collection、Object、Mesh datablock、Material、Texture，
以及交付給 Unreal 的輸出檔名。目標是讓資產在 `.blend`、匯出檔與 Unreal Content
Browser 之間能以同一名稱追蹤，並避免把僅供 Blender 整理用的內容誤匯出。

## 核心原則

1. 名稱只使用 ASCII 英文字母、數字與底線，不使用空格、連字號、句點或中文。
2. 採用 `Prefix_AssetName[_Variant][_Index]` 格式，單字使用 PascalCase，索引使用兩位數
   （例如 `A01`、`00`）。
3. Prefix 必須反映資產類型，不以 Blender 自動產生的 `.001`、`.002` 作為版本或變體。
4. 每個可匯出的 Static Mesh，其 **Object 名稱、Mesh datablock 名稱及輸出檔案的 basename
   必須完全一致**（包含大小寫）。
5. Collection 只負責場景組織。`COL_` 名稱不得成為 Unreal 資產名稱，也不得當作單一資產匯出。

## 前綴

| 類型 | 前綴 | 範例 | 說明 |
| --- | --- | --- | --- |
| Static Mesh | `SM_` | `SM_PatTat_Facade_A01` | 可匯出的靜態網格資產 |
| 完整／主材質 | `M_` | `M_WallTile_Master` | 定義完整 shader 的材質 |
| 材質實例 | `MI_` | `MI_WallTile_GreenAged` | 主材質的參數化變體 |
| Texture | `T_` | `T_WallTile_BC` | 貼圖；名稱結尾還必須包含用途後綴 |
| 自訂凸形碰撞 | `UCX_` | `UCX_SM_Railing_A01_00` | 對應 Static Mesh 的 convex collision |
| Unreal socket 輔助節點 | `SOCKET_` | `SOCKET_LampMount_00` | 應建立為 Empty，不是可渲染 mesh |
| Blender Collection | `COL_` | `COL_PatTat_Facade` | 僅供 Blender 場景組織，不輸出成資產 |

不要自行縮寫或混用前綴，例如不要使用 `MAT_`、`TEX_`、`COLLECTION_`。

## 各類型規則

### Collection

- 所有用於組織場景的 Collection 均以 `COL_` 開頭，例如 `COL_PatTat_Facade`。
- Collection 名稱可描述區域、建築或製作階段，但不取代資產名稱。
- 匯出時選取 Collection 內實際需要的 `SM_`、`UCX_` 與 `SOCKET_` 物件；不要以
  `COL_` 名稱作為 Unreal 資產或輸出檔名。
- 暫存、參考與備份 Collection 仍須使用 `COL_`，並在匯出前排除。

### Static Mesh Object 與 Mesh datablock

每一個可匯出的 mesh 必須遵守一對一同名原則：

| Blender 欄位／輸出 | 必須使用的名稱 |
| --- | --- |
| Object | `SM_PatTat_Facade_A01` |
| Object Data（Mesh datablock） | `SM_PatTat_Facade_A01` |
| 輸出檔 | `SM_PatTat_Facade_A01.fbx`（或其他核准格式的相同 basename） |
| Unreal Static Mesh | `SM_PatTat_Facade_A01` |

複製資產後必須立即同時重新命名 Object 與 Mesh datablock。例如新變體應命名為
`SM_PatTat_Facade_A02`，不可留下 `SM_PatTat_Facade_A01.001`。如果兩個 Object 共用同一個
datablock，匯出前應確認它們確實是同一資產的 instance；需要獨立輸出的變體必須先建立
single-user datablock，再依新 Object 名稱重新命名。

### Material 與材質實例

- 完整材質使用 `M_`，名稱應描述表面或用途，例如 `M_WallTile_Master`。
- 可調參數的材質變體使用 `MI_`，名稱應描述其可辨識變體，例如
  `MI_WallTile_GreenAged`。
- Blender material datablock、Object material slot 顯示的材質名稱，以及 Unreal 中對應的
  Material／Material Instance 名稱應一致。
- 不使用 `Material.001` 等 Blender 預設名稱；複製後立即依其用途命名。

### Texture 與固定後綴

Texture 使用 `T_<SurfaceOrAsset>_<Suffix>` 格式。用途後綴固定如下：

| 後綴 | 用途 | 範例 |
| --- | --- | --- |
| `_BC` | Base Color | `T_WallTile_BC` |
| `_N` | Normal | `T_WallTile_N` |
| `_ORM` | Occlusion（R）、Roughness（G）、Metallic（B）打包貼圖 | `T_WallTile_ORM` |
| `_E` | Emissive | `T_NeonSign_E` |
| `_M` | Mask | `T_Window_M` |
| `_H` | Height | `T_Cobblestone_H` |

只有下游材質確實讀取 Height 時才輸出 `_H`。不要以 `_Color`、`_Diffuse`、`_Normal`
或 `_RMA` 取代上述後綴。貼圖檔案 basename 與 Texture 名稱必須一致，例如
`T_WallTile_ORM.png` 匯入後命名為 `T_WallTile_ORM`。

### Collision

自訂凸形碰撞使用 Unreal 可辨識的格式：

```text
UCX_<完整 Static Mesh 名稱>_<兩位數序號>
```

例如 `SM_Railing_A01` 的第一、第二個 convex hull 分別為：

```text
UCX_SM_Railing_A01_00
UCX_SM_Railing_A01_01
```

Collision Object 與它的 Mesh datablock 也必須同名。碰撞物件必須與目標 `SM_` 一起輸出，
不可單獨產生 `UCX_*.fbx` 檔案。

### Socket

- 需要在 Unreal 成為 socket 的輔助節點以 `SOCKET_` 開頭，例如
  `SOCKET_LampMount_00`。
- Socket 應使用 Blender Empty，並與目標 `SM_` 一起輸出。
- 名稱須表達掛接用途；同用途有多個位置時使用兩位數序號。

## 輸出規則

1. 一個輸出檔代表一個主要 `SM_` 資產。
2. 輸出檔 basename 必須與主要 Static Mesh 的 Object 及 Mesh datablock 完全相同。
3. 同檔可包含該資產對應的 `UCX_` collision 與 `SOCKET_` Empty；它們不改變檔名。
4. `COL_` Collection、參考物件、相機、燈光及製作輔助物件不得包含於資產輸出。
5. 檔案格式由專案的匯出流程決定；無論使用 `.fbx`、`.gltf` 或其他格式，basename
   都不得改變。

正確範例：

```text
COL_PatTat_Railing                 # Blender 組織用，不作為輸出資產
├── SM_Railing_A01                 # Object
│   └── SM_Railing_A01             # Mesh datablock
├── UCX_SM_Railing_A01_00          # Collision Object 與同名 datablock
├── UCX_SM_Railing_A01_01
└── SOCKET_LampMount_00             # Empty

輸出：SM_Railing_A01.fbx
```

## 匯出前檢查清單

- [ ] Collection 皆以 `COL_` 開頭，且未被當作 Unreal 資產輸出。
- [ ] 主要 Object 與 Mesh datablock 都使用 `SM_` 前綴且完全同名。
- [ ] 輸出檔 basename 與主要 `SM_` 名稱完全一致。
- [ ] Material 使用 `M_` 或 `MI_`，不存在 `Material`、`Material.001` 等預設名稱。
- [ ] Texture 使用 `T_`，並以 `_BC`、`_N`、`_ORM`、`_E`、`_M` 或必要的 `_H` 結尾。
- [ ] Collision 依 `UCX_<完整 SM 名稱>_<序號>` 命名，Object 與 datablock 同名。
- [ ] Socket 使用 `SOCKET_` 前綴，類型為 Empty，並與對應 Static Mesh 一起輸出。
- [ ] 名稱不含空格、中文、連字號、Blender `.001` 後綴或未核准的縮寫。
