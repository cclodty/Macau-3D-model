# Macau 3D Model

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
