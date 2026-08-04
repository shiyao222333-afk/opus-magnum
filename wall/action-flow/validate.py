# -*- coding: utf-8 -*-
"""
validate.py — 格式校验员（知识→行动回流系统）
职责：校验每周清单 md 是否符合 template.md 模板。格式坏了当场报错，坏数据进不了看板。

用法：python validate.py weekly/2026W32.md
返回码：0 = 通过，1 = 不通过
"""
import re
import sys

# 四色标记（Panopticon 启发：区分"谁来做"）
COLOR_MARKS = ["🟢", "🟡", "🔴", "⚪"]
REQUIRED_SECTIONS = ["一、新提炼行动", "二、待办跟进", "三、🎯 本周最高杠杆一件事", "四、🧭 知识缺口", "五、路线进度"]


def validate(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    errors = []
    text = "\n".join(lines)

    # 1. 五节齐全
    for sec in REQUIRED_SECTIONS:
        if sec not in text:
            errors.append(f"缺章节: {sec}")

    # 2. 第一节：行动项格式（- [ ] + 四色 + 来源/依据/创建周/优先）
    section1_start = next((i for i, l in enumerate(lines) if "一、新提炼行动" in l), None)
    section1_end = next((i for i, l in enumerate(lines) if "二、待办跟进" in l), len(lines))
    if section1_start is not None:
        action_lines = [l for l in lines[section1_start + 1 : section1_end]
                        if l.strip().startswith("- [") and not l.strip().startswith("<!--")]
        for l in action_lines:
            has_color = any(m in l for m in COLOR_MARKS)
            has_source = "来源：" in l
            has_basis = "依据：" in l
            has_week = re.search(r"创建周：[A-Za-z]*\d+", l)
            has_pri = "优先：" in l
            has_docid = re.search(r"\|\s*doc_id[:：]\s*[A-Za-z0-9_-]+", l)
            if not all([has_color, has_source, has_basis, has_week, has_pri]):
                errors.append(f"行动项格式缺字段(需四色+来源+依据+创建周+优先): {l.strip()[:50]}")
            # doc_id 必填（第6类管理的前提；缺了清单页不渲染管理栏=静默失效）
            if not has_docid:
                errors.append(f"行动项缺 doc_id（第6类管理必填，从 scan.py --json 的 docs 里取）: {l.strip()[:50]}")
            # 可选字段：🔥市场验证（有则校验格式：X万播放）
            for m in re.finditer(r"🔥市场验证：([^|]+)", l):
                if not re.match(r"^\s*\d+(\.\d+)?万播放\s*$", m.group(1)):
                    errors.append(f"🔥市场验证格式错误(应为'X万播放'): {m.group(1).strip()[:20]}")

    # 3. 第三节：最高杠杆一件事
    if "**一件事：**" not in text:
        errors.append("第三节缺 '**一件事：**' 字段")

    # 4. 第四节：知识缺口表格（表头含 路线需要）
    if "路线需要" not in text or "|" not in text:
        errors.append("第四节缺知识缺口表格(需含'路线需要'列)")

    # 5. 第二节：跟进项带"已提醒第 N 周"
    section2_start = next((i for i, l in enumerate(lines) if "二、待办跟进" in l), None)
    section2_end = next((i for i, l in enumerate(lines) if "三、🎯" in l), len(lines))
    if section2_start is not None:
        follow_lines = [l for l in lines[section2_start + 1 : section2_end]
                        if l.strip().startswith("- [") and not l.strip().startswith("<!--")]
        for l in follow_lines:
            if "已提醒第" not in l or "周" not in l:
                errors.append(f"跟进项缺'已提醒第N周'标注: {l.strip()[:50]}")

    if errors:
        print(f"❌ 校验不通过 ({path})")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"✅ 校验通过 ({path})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python validate.py <周清单.md>")
        sys.exit(1)
    sys.exit(validate(sys.argv[1]))
