# 首次導入驗收閘門

只有全部項目通過並由技術美術簽名後，才可大量製作八達新邨的最終模型。

## 測試資產

從 Blender 輸出一個 1 m 測試立方體及一個代表性外牆模組，使用 FBX（或團隊批准的
Interchange 格式），並提供同一材質組的 `*_BC`、`*_N`、`*_ORM`、`*_E`。

## 驗收清單

- [ ] 在鎖定的 UE 5.4.4 開啟專案，Import Test Map 無警告載入。
- [ ] 1 m Blender 立方體對齊地圖 100 cm 尺，軸向、pivot、transform 及法線正確。
- [ ] 外牆 material instance：`_BC` → Base Color（sRGB 開）；`_N` → Normal
  （Normal compression、sRGB 關）；`_ORM` → R/G/B 分別接 AO/Roughness/Metallic
  （Masks、sRGB 關）；`_E` → Emissive Color（sRGB 視來源色彩空間）。
- [ ] 玻璃 instance 的透明度、roughness、雙面需求及排序在正反面與夜景均正確。
- [ ] 道路 instance 的比例、法線強度、roughness、積水/標線需求在斜光下正確。
- [ ] 灰卡在標準光源下沒有意外色偏；曝光固定後保存對照截圖。
- [ ] 測試攝影機構圖、近裁切、陰影、Lumen GI/reflection 與 VSM 無明顯 artifact。
- [ ] 適合的靜態網格啟用 Nanite；fallback、lightmap UV、碰撞及 LOD 行為已檢查。
- [ ] `stat unit`、`stat gpu`、`stat streaming` 在目標級別硬件符合 README 預算。
- [ ] Development 及 Shipping cook 成功，Output Log 沒有 missing asset/shader error。

簽核人：________　日期：________　測試 build/commit：________________
