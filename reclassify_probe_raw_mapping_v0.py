"""
Purpose Function Schema Probe 再分類スクリプト v0.1
作成日: 2026-08-03
目的:
  - 元のFrozen Proseファイルを一切変更せず保存
  - Raw（一次正本）とMapping-v0（初回構造化記録）を分離
  - 来歴を明確にした派生ファイルとマニフェストを生成
"""

from pathlib import Path
import re
from datetime import datetime

# ================== 設定 ==================
SRC_PATH = Path("/mnt/data/Purpose_Function_Schema_Probe_Frozen_Set_2026-07-30.md")
DEST_PATH = Path(f"/mnt/data/Purpose_Function_Schema_Probe_Raw_Mapping_Reclassification_{datetime.now().strftime('%Y-%m-%d')}.md")

# Probe抽出パターン
PROBE_PATTERN = r"(?m)^# Probe-(0[1-5])-Prose-Frozen-v(\d+)\s*$"

# =========================================

text = SRC_PATH.read_text(encoding="utf-8")

# Probeセクションを抽出
matches = list(re.finditer(PROBE_PATTERN, text))
sections = {}
for i, m in enumerate(matches):
    probe_id = m.group(1)
    version = m.group(2)
    start = m.start()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    sections[probe_id] = (version, text[start:end].strip())

# 出力準備
out = [
    "# Purpose Function Descriptive Metadata Schema Probe",
    "## Raw／Mapping-v0 再分類版（Probe-01〜05）",
    "",
    f"**再分類日：** {datetime.now().strftime('%Y年%m月%d日')}",
    "**再分類理由：** 既存のFrozen Proseから一次正本と構造化記録を分離",
    "**運用原則：** Rawを一次正本とし、来歴を維持。内容は削除・上書きしない。",
    "",
    "## Source Manifest",
    "",
    "| Probe | 一次正本 | 既存詳細版 | 状態 |",
    "|---|---|---|---|",
]

for pid in ["01", "02", "03", "04", "05"]:
    if pid not in sections:
        print(f"Warning: Probe-{pid} not found!")
        continue
        
    version, sec = sections[pid]
    raw_version = "v2" if pid == "05" else "v1"
    
    # Raw部分の抽出
    raw_match = re.search(r"(?ms)^## 原文(?:（.*?）)?\s*\n(.*?)(?=^## (?:原資料|1．状況))", sec)
    if raw_match:
        raw_content = raw_match.group(1).strip()
        raw_label = "原文"
    else:
        raw_match = re.search(r"(?ms)^## 原資料\s*\n(.*?)(?=^## 1．状況)", sec)
        raw_content = raw_match.group(1).strip() if raw_match else ""
        raw_label = "原資料"
    
    mapping_start = re.search(r"(?m)^## 1．状況", sec)
    mapping_body = sec[mapping_start.start():].strip() if mapping_start else sec
    
    out.extend([
        "",
        "---",
        "",
        f"# Probe-{pid}-Raw-{raw_version}",
        "",
        f"**Probe ID：** Probe-{pid}",
        f"**状態：** 一次正本／Raw",
        f"**由来：** 既存資料内の「{raw_label}」ブロック",
        "**注意：** 後続のMappingやSchemaに合わせて書き換えない。",
        "",
        raw_content or "（独立した原文ブロックなし。原資料を一次正本として保持）",
        "",
        f"# Probe-{pid}-Mapping-v0",
        "",
        "**状態：** 初回構造化記録／Schema前写像",
        f"**入力元：** Probe-{pid}-Raw-{raw_version}",
        "**位置づけ：** Rawを1．状況以降の見出し構造へ整理した既存詳細版。",
        "",
        mapping_body,
    ])

# 末尾の説明部分（必要に応じて追加）
out.extend([
    "",
    "---",
    "",
    "# 再分類後の比較対象",
    "",
    "今後のSchema Probeでは、Raw → Mapping-v0 → JSON Schemaの流れを分離して扱います。",
])

DEST_PATH.write_text("\n".join(out), encoding="utf-8")
print(f"✅ 完了！出力先: {DEST_PATH}")
