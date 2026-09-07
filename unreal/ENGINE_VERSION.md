# Unreal Engine 版本鎖定

本專案的正式目標版本是 **Unreal Engine 5.4.4**（Epic Launcher/vanilla build，Windows）。
`Macau3D.uproject` 的 `EngineAssociation` 保持在 `5.4`，補丁版本以本文件為準。

## 升級政策

正式生產開始後不得直接用新版 Editor 開啟主專案。升級只能在獨立分支及專案副本進行，並須：

1. 保存升級前的 Derived Data Cache 以外所有受版本控制內容及可重現的 cooked build；
2. 完整執行 `IMPORT_ACCEPTANCE.md`，重導入測試資產並比較材質通道、比例、碰撞及 Nanite；
3. 在目標級別硬件完成 Development 與 Shipping cook、Import Test Map 截圖及 GPU/CPU/串流效能比較；
4. 驗證所有 Blueprint、World Partition、Data Layer、Lumen、VSM 及自動化測試，沒有 load error；
5. 由技術美術及專案負責人批准遷移報告後，才更新本文件與 `.uproject` 並合併。

未完成上述遷移測試時，**不得升級引擎版本或 resave 生產資產**。
