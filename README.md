# 🎮 Dota 2 Gemini AI Discord Bot

A powerful, multilingual Dota 2 Discord bot that combines Google Gemini and OpenDota APIs to deliver real-time hero strategy, item builds, lane guides, meta analysis, and professional match insights — all in one place.

> 讓你在 Discord 中用中文或英文詢問 Dota 2 的任何問題，並獲得智慧型 AI 回應！

---

## 🔧 Features

| 指令 | 功能說明 |
|------|----------|
| `!hero [英雄名稱]` | 提供英雄攻略：定位、技能、對線、團戰、優劣勢等 |
| `!build [英雄名稱]` | 根據角色與時機提供最佳出裝建議 |
| `!counter [英雄名稱]` | 告訴你如何克制或被誰克制 |
| `!lane [英雄名稱]` | 對線技巧、視野、補刀與走位建議 |
| `!combo [英雄名稱]` | 技能連招順序、配裝、時機 |
| `!meta` | 最新版本的強勢英雄、熱門戰術、改動分析 |
| `!pro [英雄名稱]` | 擷取 OpenDota API，給你英雄在職業賽中的操作與趨勢 |
| `!discuss [問題]` | 提問任何 Dota 2 相關問題，AI 將提供完整回答 |
| `!commands` | 顯示所有支援指令 |

---

## 🤖 技術架構

- [x] Discord Bot (Python `discord.py`)
- [x] Google Gemini 1.5 Pro（語意理解與自然語言生成）
- [x] OpenDota API（拉取英雄數據 / 比賽紀錄）
- [x] Hero alias 辨識支援中英文（`斧王`, `axe`, `ax`...）
- [x] replit雲端架設 

---

## 🚀 啟動流程

replit run bot.py
