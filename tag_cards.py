# -*- coding: utf-8 -*-
"""Parse BanG Dream card texts into filterable effect tags."""
import json
import os
import re
import sys
from collections import Counter, defaultdict

INPUT_FILE = "data/clean_cards.json"
OUTPUT_FILE = "web/cards.json"
STATS_FILE = "web/tag_stats.json"

BANDS = [
    "Poppin'Party",
    "Afterglow",
    "Pastel＊Palettes",
    "Roselia",
    "ハロー、ハッピーワールド！",
    "RAISE A SUILEN",
    "Morfonica",
    "MyGO!!!!!",
    "Ave Mujica",
    "CRYCHIC",
    "夢限大みゅーたいぷ",
]

BAND_ALIASES = {
    "Poppin’Party": "Poppin'Party",
    "Pastel Palettes": "Pastel＊Palettes",
}

ANNIVERSARY = "Anniversary"
MUSIC = "音楽"

TRIGGER_PRIMARY = [
    ("gate", "門"),
    ("salvage", "扉"),
    ("treasure", "金"),
    ("draw", "袋"),
    ("standby", "スタンバイ"),
    ("choice", "チョイス"),
    ("stock", "ストック"),
    ("shot", "ショット"),
    ("soul", "ソウル"),
]

# BottleNeko printed values that are clearly wrong.
POWER_OVERRIDES = {
    "BD/WE49-P10": 2000,  # Lv0/C0 listed as 6500; shops/print is 2000
}

# 他のキャラ1枚につき／枚数×500 → assume 4 other chars on stage.
STAGE_COUNT_ASSUME = 4
STAGE_X500_BONUS = 2000

BACKUP_EXTRA_RULES = [
    ("clock_kick", "送鐘", re.compile(r"クロック置場に置く")),
    ("heal", "救鐘", re.compile(r"自分のクロック.{0,24}控え室")),
    ("salvage", "回收", re.compile(r"手札に戻(?:す|し)")),
    ("mill", "削牌", re.compile(r"相手の山札")),
    ("reveal", "公開", re.compile(r"公開")),
    ("shuffle", "洗回牌庫", re.compile(r"山札に戻し")),
    ("soul", "魂", re.compile(r"ソウル")),
    ("reverse", "倒", re.compile(r"【リバース】")),
    ("bottom", "底牌", re.compile(r"山札の下")),
    ("stock", "庫", re.compile(r"ストック")),
    ("power", "加攻", re.compile(r"パワーを[＋+]")),
]


def normalize_trait(trait):
    if not trait:
        return None
    trait = trait.strip()
    if trait in {"-", "－", "―", ""}:
        return None
    return BAND_ALIASES.get(trait, trait)


def trait_kind(trait):
    trait = normalize_trait(trait)
    if not trait:
        return None
    if trait == MUSIC:
        return "music"
    if trait == ANNIVERSARY:
        return "anniversary"
    if trait in BANDS:
        return "band"
    return "other"


def primary_trigger(icons):
    icons = [normalize_trigger_icon(x) for x in (icons or [])]
    icons = [x for x in icons if x]
    for key, label in TRIGGER_PRIMARY:
        if key in icons:
            return {"key": key, "label": label}
    return None


def normalize_trigger_icon(icon):
    if not icon:
        return None
    icon = str(icon).strip().lower()
    if icon in {"none", "－", "-", "―"}:
        return None
    if "salvage" in icon:
        return "salvage"
    if icon in {"soul", "gate", "treasure", "draw", "standby", "choice", "stock", "shot"}:
        return icon
    return icon


def normalize_text(text):
    if not text:
        return text
    labels = {
        "soul": "【ソウル】",
        "salvage": "【扉】",
        "gate": "【門】",
        "treasure": "【金】",
        "draw": "【袋】",
        "standby": "【スタンバイ】",
        "stock": "【ストック】",
        "shot": "【ショット】",
        "bounce": "【バウンス】",
        "choice": "【チョイス】",
    }

    def repl_img(match):
        return labels.get(match.group(1).lower(), f"【{match.group(1)}】")

    text = re.sub(
        r'<img[^>]*(?:_partimages/|/)([a-z]+)\.gif[^>]*>',
        repl_img,
        text,
        flags=re.I,
    )
    text = re.sub(
        r"\[\[([a-z]+)\.gif\]\]",
        lambda m: labels.get(m.group(1).lower(), m.group(0)),
        text,
        flags=re.I,
    )
    return text


def split_abilities(text):
    if not text:
        return []
    cleaned = re.sub(r"（[^）]*(?:\.gif|トリガーした時)[^）]*）", "", text)
    parts = re.split(r"(?=【(?:永|自|起)】)", cleaned)
    return [p.strip() for p in parts if p.strip()]


def extract_pick_chunks(ability):
    chunks = []
    patterns = [
        r"山札を見て([^。]*?)(?:選んで|選び)",
        r"まで見て([^。]*?)(?:手札に加え|ストック置場|控え室に置く)",
        r"それらのカードの([^。]*?)(?:選び|選んで)",
        r"そのカードが([^。]{0,40})なら手札に加え",
        r"公開.{0,60}手札に加え",
        r"控え室の([^。]*?)(?:選び|選んで)",
        r"クロック(?:置場)?の([^。]*?)(?:選び|選んで)",
        r"クロックを([^。]*?)選び",
    ]
    for pat in patterns:
        for match in re.finditer(pat, ability):
            chunks.append(match.group(1) if match.lastindex else match.group(0))
    return chunks


def classify_pick_targets(chunks, fallback_ability=""):
    targets = set()
    bands = set()
    sources = chunks if chunks else ([fallback_ability] if fallback_ability else [])
    for chunk in sources:
        traits = [normalize_trait(t) for t in re.findall(r"《([^》]+)》", chunk)]
        traits = [t for t in traits if t]
        if re.search(r"CX|クライマックス", chunk):
            targets.add("cx")
        if re.search(r"「[^」]+」", chunk) and not re.search(r"CX置場に「", chunk):
            if re.search(r"控え室の「|手札の「|山札[^。]{0,20}「", chunk) or "」を1枚" in chunk:
                targets.add("named")
        if traits:
            for trait in traits:
                kind = trait_kind(trait)
                if kind == "music":
                    targets.add("music")
                elif kind == "anniversary":
                    targets.add("anniversary")
                elif kind == "band":
                    targets.add("band")
                    bands.add(trait)
                else:
                    targets.add("other")
                    bands.add(trait)
        elif re.search(r"キャラ|カード|\d枚", chunk):
            targets.add("any_char")
    return targets, bands


WHEN_RULES = [
    ("play", "進場", re.compile(r"手札から舞台に置かれた時")),
    ("leave", "離場", re.compile(r"舞台から控え室に置かれた時")),
    ("reverse", "倒時", re.compile(r"(?:バトル中の)?このカードが【リバース】した時")),
    ("battle_reverse", "對手倒置", re.compile(r"このカードのバトル相手.{0,24}【リバース】した時")),
    ("attack", "攻擊", re.compile(r"アタックした時|アタックの終わりに|アタックフェイズ")),
    ("cx", "CX時", re.compile(r"CX置場に|クライマックス置場に")),
]


BATTLE_REVERSE_RE = re.compile(r"このカードのバトル相手.{0,24}【リバース】した時")


def search_when(ability):
    found = []
    for key, label, pattern in WHEN_RULES:
        if pattern.search(ability):
            found.append({"key": key, "label": label})
    return found


def look_count(ability):
    for pat in (
        r"上から(\d+)枚まで見て",
        r"上から(\d+)枚見て",
        r"上から(\d+)枚までを[、,]?公開",
        r"上から(\d+)枚を公開",
        r"上から(\d+)枚までを、公開",
    ):
        match = re.search(pat, ability)
        if match:
            return int(match.group(1))
    return None


def classify_search(ability):
    result = {
        "from": set(),
        "targets": set(),
        "bands": set(),
        "when": [],
        "look_n": None,
    }
    has_add = (
        "手札に加え" in ability
        or "選んで相手に見せ" in ability
        or re.search(r"ストック置場に置", ability)
    )
    brainstorm = "集中" in ability and re.search(r"めくり", ability)
    deck_full = "山札を見て" in ability and has_add
    deck_look = (not deck_full) and has_add and (
        "まで見て" in ability
        or bool(re.search(r"山札[のを上から]{1,10}\d+枚見て", ability))
        or bool(re.search(r"山札の上から", ability) and re.search(r"公開", ability))
    )
    body = re.sub(r"［[^］]*］", "", ability)
    salvage = bool(
        re.search(r"控え室の(?:《|キャラ|CX|カード|「)", body)
        and re.search(r"手札に戻(?:す|し)|手札に加え", body)
    )
    clock_salvage = bool(
        re.search(r"クロック(?:置場)?を?\d枚選び、手札に戻", body)
        or re.search(r"クロックの.{0,32}手札に戻", body)
    )

    if brainstorm:
        result["from"].add("brainstorm")
    if deck_full and not brainstorm:
        result["from"].add("deck")
    if deck_look and not brainstorm:
        result["from"].add("top")
    if salvage:
        result["from"].add("waiting")
    if clock_salvage:
        result["from"].add("clock")

    if not result["from"]:
        return result

    if result["from"] & {"deck", "top", "waiting", "clock"}:
        result["when"] = search_when(ability)
        if result["from"] & {"deck", "top"}:
            result["look_n"] = look_count(ability)

    chunks = extract_pick_chunks(ability)
    fallback = ""
    if not chunks and ("waiting" in result["from"] or "clock" in result["from"] or brainstorm):
        fallback = ""
    targets, bands = classify_pick_targets(chunks, fallback)
    if not targets and (salvage or clock_salvage or brainstorm):
        targets.add("any_char")
    result["targets"] |= targets
    result["bands"] |= bands
    return result


def _normalize_power_text(ability):
    return ability.replace("パワーを+", "パワーを＋").replace("パワーを-", "パワーを－")


def _is_self_power_ability(text):
    if re.search(r"助太刀\d+", text):
        return False
    if "このカードのパワー" in text:
        return True
    if re.search(r"あなたのキャラすべてに", text) and "他のあなたの" not in text:
        return True
    return False


def _non_stage_context(text):
    return any(
        token in text
        for token in (
            "相手のキャラ",
            "控え室",
            "マーカー",
            "クロック",
            "ストック",
            "それらのカード",
            "思い出",
        )
    )


def stage_count_bonus(text):
    """Estimate 台面枚数× / 1枚につき self-buffs. ×500 → +2000."""
    for match in re.finditer(r"1枚につき、(?:このカードの)?パワーを＋(\d+)", text):
        ctx = text[max(0, match.start() - 48):match.end()]
        if _non_stage_context(ctx):
            continue
        unit = int(match.group(1))
        return STAGE_X500_BONUS if unit == 500 else unit * STAGE_COUNT_ASSUME, unit
    if "パワーを＋Ｘ" in text or "パワーを＋X" in text:
        for match in re.finditer(r"Ｘは([^。]{0,80})枚数×(\d+)", text):
            if _non_stage_context(match.group(1)):
                continue
            unit = int(match.group(2))
            return STAGE_X500_BONUS if unit == 500 else unit * STAGE_COUNT_ASSUME, None
    return None, None


def self_power_sort_bonus(ability):
    text = _normalize_power_text(ability)
    if not _is_self_power_ability(text):
        return 0
    estimated, per_unit = stage_count_bonus(text)
    flats = [int(n) for n in re.findall(r"パワーを＋(\d+)", text)]
    if estimated is not None:
        if per_unit is not None:
            flats = [n for n in flats if n != per_unit]
        return estimated + sum(flats)
    return sum(flats)


def classify_power(ability):
    if re.search(r"助太刀\d+", ability):
        return None
    text = ability.replace("パワーを+", "パワーを＋").replace("パワーを-", "パワーを－")
    plus = "パワーを＋" in text
    minus = "パワーを－" in text
    if not plus and not minus:
        return None

    traits = [normalize_trait(t) for t in re.findall(r"《([^》]+)》", text)]
    traits = [t for t in traits if t]
    unrestricted = False
    if re.search(r"あなたのキャラすべてに", text) and not re.search(r"あなたの《", text):
        unrestricted = True
    if re.search(r"自分のキャラを\d枚(?:まで)?選び", text) and not re.search(r"《[^》]+》のキャラ", text):
        unrestricted = True
    if "このカードのパワー" in text and not traits:
        unrestricted = True
    if not traits:
        unrestricted = True

    bonuses = [int(n) for n in re.findall(r"パワーを＋(\d+)", text)]
    bonus_x = bool(re.search(r"パワーを＋Ｘ", text))

    return {
        "plus": plus,
        "minus": minus,
        "unrestricted": unrestricted,
        "traits": traits,
        "bonuses": bonuses,
        "bonus_x": bonus_x,
    }


def classify_backup(text):
    if "助太刀" not in text:
        return None
    match = re.search(r"助太刀(\d+)\s*レベル(\d+)\s*［([^］]+)］", text)
    if not match:
        return {
            "power": None,
            "level": None,
            "stock": None,
            "extra": "『助太刀』を使った時" in text,
            "extra_kinds": [],
        }
    cost = match.group(3)
    stock_match = re.search(r"\((\d+)\)", cost)
    extra_clause = ""
    extra_match = re.search(r"【自】[^【]*『助太刀』を使った時[^【]*", text)
    if extra_match:
        extra_clause = extra_match.group(0)
    extra_kinds = []
    if extra_clause:
        for key, label, pattern in BACKUP_EXTRA_RULES:
            if pattern.search(extra_clause):
                extra_kinds.append({"key": key, "label": label})
    return {
        "power": int(match.group(1)),
        "level": int(match.group(2)),
        "stock": int(stock_match.group(1)) if stock_match else 0,
        "extra": bool(extra_clause),
        "extra_kinds": extra_kinds,
    }


def classify_brainstorm(ability):
    if "集中" not in ability:
        return None
    payoff = set()
    if "手札に戻す" in ability:
        payoff.add("salvage")
    if re.search(r"引く", ability):
        payoff.add("draw")
    if "ストック" in ability:
        payoff.add("stock")
    if "クロック" in ability:
        payoff.add("clock")
    if "パワー" in ability:
        payoff.add("power")
    if "山札を見て" in ability:
        payoff.add("search")
    if "【スタンド】" in ability or "スタンド" in ability:
        payoff.add("stand")
    return payoff


def extract_cx_combo_names(text, cx_names):
    if "CXコンボ" not in (text or ""):
        return []
    names = []
    for name in re.findall(r"「([^」]+)」", text or ""):
        if name in cx_names and name not in names:
            names.append(name)
    return names


def merge_power(acc, item):
    if not item:
        return acc
    acc["plus"] = acc["plus"] or item["plus"]
    acc["minus"] = acc["minus"] or item["minus"]
    acc["unrestricted"] = acc["unrestricted"] or item["unrestricted"]
    acc["bonus_x"] = acc.get("bonus_x") or item.get("bonus_x")
    for trait in item["traits"]:
        if trait not in acc["traits"]:
            acc["traits"].append(trait)
    for n in item.get("bonuses") or []:
        if n not in acc["bonuses"]:
            acc["bonuses"].append(n)
    return acc


def tag_card(card, cx_by_name):
    text = normalize_text(card.get("text") or "")
    abilities = split_abilities(text)
    if not abilities and text.strip() and text.strip() not in {"-", "－"}:
        abilities = [text]

    search_from = set()
    search_targets = set()
    search_bands = set()
    search_when_keys = []
    look_ns = []
    power = {"plus": False, "minus": False, "unrestricted": False, "traits": [], "bonuses": [], "bonus_x": False}
    power_sort_bonus = 0
    brainstorm_payoff = set()

    for ability in abilities:
        search = classify_search(ability)
        search_from |= search["from"]
        search_targets |= search["targets"]
        search_bands |= search["bands"]
        for item in search.get("when") or []:
            if item["key"] not in {x["key"] for x in search_when_keys}:
                search_when_keys.append(item)
        if search.get("look_n"):
            if search["look_n"] not in look_ns:
                look_ns.append(search["look_n"])
        power = merge_power(power, classify_power(ability))
        power_sort_bonus += self_power_sort_bonus(ability)
        payoff = classify_brainstorm(ability)
        if payoff:
            brainstorm_payoff |= payoff

    backup = classify_backup(text)
    cx_names = extract_cx_combo_names(text, cx_by_name)
    combo_triggers = []
    seen_trig = set()
    for name in cx_names:
        for cx in cx_by_name.get(name, []):
            trig = primary_trigger(cx.get("trigger"))
            if trig and trig["key"] not in seen_trig:
                seen_trig.add(trig["key"])
                combo_triggers.append(trig)

    own_trigger = primary_trigger(card.get("trigger"))
    own_traits = [normalize_trait(t) for t in (card.get("traits") or [])]
    own_traits = [t for t in own_traits if t]

    power_kinds = set()
    if power["plus"] or power["minus"]:
        if power["unrestricted"]:
            power_kinds.add("any")
        for trait in power["traits"]:
            kind = trait_kind(trait)
            if kind == "music":
                power_kinds.add("music")
            elif kind == "anniversary":
                power_kinds.add("anniversary")
            elif kind == "band":
                power_kinds.add("band")
            elif kind:
                power_kinds.add("other")

    tagged = dict(card)
    tagged["text"] = text
    if card.get("id") in POWER_OVERRIDES:
        tagged["power"] = POWER_OVERRIDES[card["id"]]
    tagged["own_traits"] = own_traits
    tagged["own_bands"] = [t for t in own_traits if trait_kind(t) == "band"]
    tagged["cx_combo"] = "CXコンボ" in text
    tagged["cx_combo_names"] = cx_names
    tagged["cx_combo_triggers"] = combo_triggers
    tagged["climax_trigger"] = own_trigger if card.get("type") == "クライマックス" else None
    tagged["filter_triggers"] = []
    if tagged["climax_trigger"]:
        tagged["filter_triggers"].append(tagged["climax_trigger"])
    tagged["filter_triggers"].extend(combo_triggers)
    tagged["search_from"] = sorted(search_from)
    tagged["search_targets"] = sorted(search_targets)
    tagged["search_bands"] = sorted(search_bands)
    tagged["search_when"] = search_when_keys
    tagged["look_n"] = sorted(look_ns)
    tagged["power_fx"] = {
        "plus": power["plus"],
        "minus": power["minus"],
        "unrestricted": power["unrestricted"],
        "traits": power["traits"],
        "kinds": sorted(power_kinds),
        "bands": [t for t in power["traits"] if trait_kind(t) == "band"],
        "bonuses": sorted(power["bonuses"]),
        "bonus_x": power["bonus_x"],
        "sort_bonus": power_sort_bonus,
    }
    tagged["backup"] = backup
    tagged["brainstorm"] = bool(brainstorm_payoff) or ("集中" in text)
    tagged["brainstorm_payoff"] = sorted(brainstorm_payoff)
    tagged["resonate"] = "共鳴" in text
    tagged["experience"] = "経験" in text
    tagged["battle_reverse"] = bool(BATTLE_REVERSE_RE.search(text))
    return tagged


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    with open(INPUT_FILE, encoding="utf-8") as f:
        cards = json.load(f)

    cx_by_name = defaultdict(list)
    for card in cards:
        if card.get("type") == "クライマックス":
            cx_by_name[card.get("name")].append(card)

    tagged = [tag_card(card, cx_by_name) for card in cards]

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(tagged, f, ensure_ascii=False, indent=2)
    data_js = os.path.join(os.path.dirname(OUTPUT_FILE), "cards-data.js")
    with open(data_js, "w", encoding="utf-8") as f:
        f.write("window.CARDS = ")
        json.dump(tagged, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    stats = {
        "total": len(tagged),
        "cx_combo": sum(1 for c in tagged if c["cx_combo"]),
        "brainstorm": sum(1 for c in tagged if c["brainstorm"]),
        "backup": sum(1 for c in tagged if c["backup"]),
        "search_from": dict(Counter(src for c in tagged for src in c["search_from"])),
        "search_targets": dict(Counter(t for c in tagged for t in c["search_targets"])),
        "power_kinds": dict(Counter(k for c in tagged for k in c["power_fx"]["kinds"])),
        "combo_triggers": dict(
            Counter(t["label"] for c in tagged for t in c["cx_combo_triggers"])
        ),
        "climax_triggers": dict(
            Counter((c["climax_trigger"] or {}).get("label") for c in tagged if c["climax_trigger"])
        ),
        "search_when": dict(Counter(w["key"] for c in tagged for w in c.get("search_when") or [])),
        "look_n": dict(Counter(n for c in tagged for n in c.get("look_n") or [])),
        "backup_extra": sum(1 for c in tagged if c["backup"] and c["backup"]["extra"]),
        "battle_reverse": sum(1 for c in tagged if c.get("battle_reverse")),
        "experience": sum(1 for c in tagged if c.get("experience")),
        "resonate": sum(1 for c in tagged if c.get("resonate")),
    }
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"Wrote {len(tagged)} cards to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
