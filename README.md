# Macau 3D Model — 法線與烘焙管線

本儲存庫提供一套**明確、可重現**的 Blender → Unreal 靜態網格流程。它不讓 FBX 輸出器或 Unreal 臨時決定三角化：正式輸出前會在 Blender 複製物件、套用 modifier、套用固定設定的 Triangulate modifier，再以同一份 FBX 在兩端驗證。

## 安裝 Blender 工具

1. 在 Blender 的 **Edit → Preferences → Add-ons → Install from Disk** 選取本儲存庫打包出的 `macau_pipeline.zip`（zip 根目錄必須是 `macau_pipeline/`）。開發環境也可直接把 `macau_pipeline/` 複製到 Blender 的 `scripts/addons/`。
2. 啟用 **Macau Normal & Bake Pipeline**。
3. 在 3D Viewport 的 Sidebar 開啟 **Macau Pipeline**。

建議先保留一份未破壞的 high/low/cage 工作檔，再在輸出用 Collection 執行工具。

## 標準流程

### 1. Low-poly shading

選取 low-poly 後按 **Prepare Selected Meshes**：

- 面設為 smooth shading。
- 依 `Sharp angle` 標記 hard/sharp edge。
- 由目前 split normals 寫入 custom normals。
- 建立名為 `MACAU_TRIANGULATE` 的 Triangulate modifier；quad 使用 Fixed、ngon 使用 Beauty，並保留 custom normals。

需要硬邊的 UV seam 應由美術人員明確標記；不要只靠角度規則。硬邊通常也應拆 UV，避免烘焙跨越不連續切線基底。

### 2. Bake 設定留檔

在面板指定 low-poly、high-poly 與可選 cage，填寫 cage extrusion、max ray distance、normal space，然後按 **Save Bake Manifest**。工具會把以下內容同時寫到場景 custom property 與 blend 檔旁的 `*.bake.json`：

- high、low、cage 物件名稱；
- tangent-space / cage / ray distance；
- 三角化 quad、ngon、minimum vertices 與 keep normals 設定；
- Blender 版本與 UTC 時間。

烘焙時，請使用 manifest 內的 low-poly（三角化已固定）與 cage。法線貼圖在 Blender Image Texture 節點必須設為 **Non-Color**，Normal Map 節點使用 **Tangent Space**；Unreal 使用相同 tangent-space 法線，若方向不一致只在已確認格式差異後統一處理綠色通道，不要逐資產猜測。

### 3. 固定三角化並輸出 FBX

按 **Freeze Triangulation & Export FBX**。工具會：

1. 複製選取物件到 `MACAU_EXPORT` collection（來源不被破壞）；
2. 套用複製物件的全部 modifier；
3. 確保 Triangulate 是最後且已被實際套用；
4. 以 FBX `Smoothing = Edge`、`Tangent Space = on` 輸出 normals 與 tangents；
5. 留下匯出副本，供 Blender 回讀 FBX 後逐三角形檢查。

不要再由 Unreal 或另一個 DCC 重新三角化正式檔。Blender 驗證時把 FBX 匯回乾淨場景，檢查 normal map 下的接縫和斜面；Unreal 也必須使用同一份 FBX。

### 4. Unreal A/B 導入與 preset

在 Unreal Editor 的 Python console 執行：

```python
exec(open(r"/absolute/path/to/unreal/import_presets.py", encoding="utf-8").read())
compare_imports(r"/absolute/path/asset.fbx", "/Game/MeshValidation")
```

這會建立兩份測試資產：

- `_ImportedNT`：Import Normals and Tangents（管線預設）。
- `_RecomputedNT`：Compute Normals（僅供比較）。

在相同材質、相同 normal map、LOD 0 下檢查硬邊、UV seam、斜面與鏡像位置。確認匯入結果後，用 `import_production(...)` 正式匯入；正式 preset 明確設定 `import_mesh_lo_ds=False`、`remove_degenerates=False`、`NORMAL_IMPORT_METHOD=IMPORT_NORMALS_AND_TANGENTS`，避免引擎靜默改寫幾何或切線。

### 5. 資產稽核

按 **Audit Selected Meshes**。報告會列在 Blender Console，並寫入 Text datablock `Macau Asset Audit`。以下任何項目都必須在交付前清零：

- 負 scale / mirrored transform determinant；
- custom normals 缺失；
- 重疊面（相同 vertex set）；
- 退化三角形；
- 未套用 modifier（輸出副本除外）。

可在命令列/CI 執行：

```bash
blender project.blend --background --python-expr "import bpy, macau_pipeline; macau_pipeline.register(); macau_pipeline._background_audit()"
```

發現負 scale 時，不要只把數值改成正數；先 **Apply Scale**，再檢查面方向與鏡像區域的 normals。重疊面與退化三角形應回到網格拓撲修正，而不是依靠 Unreal 的 `Remove Degenerates`。

## 驗收清單

- [ ] sharp edges 與 UV seam 經人工檢查，smooth/custom normals 已保存。
- [ ] `.bake.json` 與 cage 一併版本控制，距離足以包覆 high-poly 且不擊中鄰件。
- [ ] normal map 使用一致 tangent space 與 Non-Color 資料。
- [ ] Triangulate 已在 Blender 實際套用；Blender 回讀與 Unreal LOD 0 三角形一致。
- [ ] FBX 包含 normals/tangents；A/B 測試結果已記錄並選定正式 preset。
- [ ] Audit 無負 scale、鏡像法線、重疊面、退化三角形及未套用 modifier。
