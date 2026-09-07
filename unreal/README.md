# Macau Unreal 專案

## 首次建立

1. 安裝鎖定的 UE 版本（見 `ENGINE_VERSION.md`），以該版本開啟 `Macau3D.uproject`。
2. 在 Editor 啟用 Python 後，開啟 **Output Log**，執行：
   `py "<repo>/unreal/Content/Python/setup_import_test.py"`
3. 腳本會建立並保存 `M_Exterior_Master`、`M_Glass_Master`、`M_Road_Master` 和
   `/Game/Macau/Maps/ImportTestMap`。把新產生的 `.uasset` / `.umap` 加入版本控制。
4. 導入測試資產，按 `IMPORT_ACCEPTANCE.md` 簽核；通過前禁止批量製作八達新邨最終模型。

## Content 規則

| 路徑 | 用途 |
| --- | --- |
| `Architecture` | 建築外殼及模組 |
| `Street` | 道路、行人路及街景組件 |
| `Props` | 可重用小型物件 |
| `Materials` | Master、instance 及 material function |
| `Textures` | `_BC`、`_N`、`_ORM`、`_E` 貼圖 |
| `Maps` | Import Test 及 production World Partition maps |
| `Blueprints` | 專案 Blueprint |

資產命名使用 `SM_`、`M_`、`MI_`、`T_`、`BP_` 前綴。Blender 以厘米對應 UE 單位
（1 m = 100 uu），套用 transform 後輸出，正面為 +X、上方為 +Z。

## 目標平台及預算

基準目標是 **Windows 10/11、DX12 SM6、6 核 CPU、16 GB RAM、6 GB VRAM、
1920×1080、60 fps**。設定以此中階目標機為準，而非高階開發機：GPU 16.6 ms、
game thread 8 ms、draw thread 8 ms；串流池 2 GB，常駐場景貼圖目標不超過
1.6 GB。每次 milestone 必須在該級別機器使用 packaged Shipping build profiling。

預設使用 Lumen software tracing（不用硬件 RT）、Virtual Shadow Maps、Nanite 與
texture streaming。建築及高面數不透明靜態網格應啟用 Nanite；玻璃、masked/WPO
資產先以非 Nanite 路徑驗證。大型 production map 必須由 **Open World** 模板建立，
保留 World Partition/One File Per Actor；Import Test Map 很小，刻意不用 streaming，
避免測試物件未載入。World Partition cell size/HLOD 要用實際街區 traversal 測試後決定。
