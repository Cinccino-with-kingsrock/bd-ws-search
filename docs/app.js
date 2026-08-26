const FILTERS = {
  types: [
    { value: "キャラ", label: "角色" },
    { value: "イベント", label: "事件" },
    { value: "クライマックス", label: "高潮" },
  ],
  levels: [
    { value: "0", label: "0" },
    { value: "1", label: "1" },
    { value: "2", label: "2" },
    { value: "3", label: "3" },
  ],
  colors: [
    { value: "yellow", label: "黃", cls: "yellow" },
    { value: "green", label: "綠", cls: "green" },
    { value: "red", label: "紅", cls: "red" },
    { value: "blue", label: "藍", cls: "blue" },
  ],
  ownBands: [
    { value: "Poppin'Party", label: "PoPiPa" },
    { value: "Afterglow", label: "Afterglow" },
    { value: "Pastel＊Palettes", label: "PasuPare" },
    { value: "Roselia", label: "Roselia" },
    { value: "ハロー、ハッピーワールド！", label: "HHW" },
    { value: "RAISE A SUILEN", label: "RAS" },
    { value: "Morfonica", label: "Morfonica" },
    { value: "MyGO!!!!!", label: "MyGO" },
    { value: "Ave Mujica", label: "Ave Mujica" },
    { value: "CRYCHIC", label: "CRYCHIC" },
    { value: "夢限大みゅーたいぷ", label: "夢限大" },
    { value: "Anniversary", label: "周年" },
  ],
  triggers: [
    { value: "soul", label: "ソウル" },
    { value: "gate", label: "門" },
    { value: "salvage", label: "扉" },
    { value: "treasure", label: "金" },
    { value: "draw", label: "袋" },
    { value: "standby", label: "スタンバイ" },
    { value: "choice", label: "チョイス" },
    { value: "stock", label: "ストック" },
    { value: "shot", label: "ショット" },
  ],
  cxCombo: [
    { value: "yes", label: "只要 CX コンボ" },
  ],
  searchFrom: [
    { value: "deck", label: "牌庫檢索" },
    { value: "top", label: "頂牌檢索" },
    { value: "waiting", label: "等待室回收" },
    { value: "clock", label: "Clock 回收" },
    { value: "brainstorm", label: "集中附帶" },
  ],
  searchWhen: [
    { value: "play", label: "進場" },
    { value: "leave", label: "離場" },
    { value: "attack", label: "攻擊" },
    { value: "reverse", label: "自己倒置" },
    { value: "battle_reverse", label: "對手倒置" },
    { value: "cx", label: "CX時" },
  ],
  lookN: [
    { value: "5", label: "五找" },
    { value: "4", label: "四找" },
    { value: "3", label: "三找" },
    { value: "2", label: "二找" },
    { value: "1", label: "一找" },
  ],
  searchTargets: [
    { value: "music", label: "音樂標籤" },
    { value: "band", label: "綁團名" },
    { value: "anniversary", label: "周年" },
    { value: "any_char", label: "不限標籤" },
    { value: "named", label: "指定卡名" },
    { value: "cx", label: "CX" },
  ],
  powerKinds: [
    { value: "music", label: "看音樂" },
    { value: "band", label: "看團名" },
    { value: "anniversary", label: "看周年" },
    { value: "any", label: "不限標籤" },
  ],
  atkBands: [
    { value: "0-1500", label: "0–1500" },
    { value: "2000-2500", label: "2000–2500" },
    { value: "3000-4500", label: "3000–4500" },
    { value: "5000-7000", label: "5000–7000" },
    { value: "8000-9500", label: "8000–9500" },
    { value: "10000", label: "10000+" },
  ],
  backup: [
    { value: "any", label: "助太刀" },
    { value: "stock0", label: "代價 0" },
    { value: "stock1", label: "代價 1" },
    { value: "extra", label: "有額外效果" },
    { value: "plain", label: "純加攻" },
  ],
  backupExtra: [
    { value: "clock_kick", label: "送鐘" },
    { value: "heal", label: "救鐘" },
    { value: "salvage", label: "回收" },
    { value: "mill", label: "削牌" },
    { value: "reveal", label: "公開" },
    { value: "shuffle", label: "洗回牌庫" },
    { value: "soul", label: "魂" },
    { value: "reverse", label: "倒" },
    { value: "power", label: "額外加攻" },
  ],
  brainstorm: [
    { value: "yes", label: "集中" },
    { value: "salvage", label: "集中→回收" },
    { value: "draw", label: "集中→抽" },
    { value: "search", label: "集中→檢索" },
    { value: "power", label: "集中→加攻" },
  ],
  mechanics: [
    { value: "battle_reverse", label: "對手倒置" },
    { value: "experience", label: "経験" },
    { value: "resonate", label: "共鳴" },
  ],
};

const selected = Object.fromEntries(Object.keys(FILTERS).map((k) => [k, new Set()]));
let cards = [];

const SORT_FIELDS = [
  { value: "", label: "（無）" },
  { value: "level", label: "等級" },
  { value: "cost", label: "費用" },
  { value: "power", label: "攻擊力（含加攻）" },
  { value: "soul", label: "靈魂" },
  { value: "color", label: "顏色" },
  { value: "type", label: "種類" },
  { value: "name", label: "卡名" },
  { value: "id", label: "編號" },
  { value: "rare", label: "稀有度" },
];
const COLOR_RANK = { yellow: 0, green: 1, red: 2, blue: 3 };
const TYPE_RANK = { "キャラ": 0, "イベント": 1, "クライマックス": 2 };
const DEFAULT_SORT = [
  ["level", "asc"],
  ["power", "desc"],
  ["id", "asc"],
];

function fillSortSelects() {
  for (const n of [1, 2, 3]) {
    const field = document.getElementById(`sort${n}`);
    const dir = document.getElementById(`dir${n}`);
    field.innerHTML = SORT_FIELDS.map((f) => `<option value="${f.value}">${f.label}</option>`).join("");
    dir.innerHTML = `<option value="asc">升</option><option value="desc">降</option>`;
    field.value = DEFAULT_SORT[n - 1][0];
    dir.value = DEFAULT_SORT[n - 1][1];
    field.addEventListener("change", apply);
    dir.addEventListener("change", apply);
  }
}

function includeUnbound() {
  return document.getElementById("includeUnbound").checked;
}

function matchesTraitFilter(selectedSet, cardValues, unboundKey) {
  if (selectedSet.size === 0) return true;
  const values = cardValues || [];
  const specific = [...selectedSet].filter((v) => v !== unboundKey);
  const wantsUnbound = selectedSet.has(unboundKey);
  const hasSpecific = specific.some((v) => values.includes(v));
  const hasUnbound = values.includes(unboundKey);
  if (specific.length && wantsUnbound) return hasSpecific || hasUnbound;
  if (specific.length) return hasSpecific || (includeUnbound() && hasUnbound);
  return hasUnbound;
}

function renderChips() {
  for (const [key, options] of Object.entries(FILTERS)) {
    const host = document.querySelector(`[data-filter="${key}"]`);
    host.innerHTML = "";
    for (const opt of options) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = `chip ${opt.cls || ""}`;
      btn.textContent = opt.label;
      btn.addEventListener("click", () => {
        if (selected[key].has(opt.value)) selected[key].delete(opt.value);
        else selected[key].add(opt.value);
        btn.classList.toggle("on");
        apply();
      });
      host.appendChild(btn);
    }
  }
}

function hasAny(set, values) {
  if (set.size === 0) return true;
  return values.some((v) => set.has(String(v)));
}

function matches(card) {
  const q = document.getElementById("q").value.trim().toLowerCase();
  if (q) {
    const blob = `${card.id} ${card.name} ${card.text || ""}`.toLowerCase();
    if (!blob.includes(q)) return false;
  }
  if (!hasAny(selected.types, [card.type])) return false;
  if (!hasAny(selected.levels, [card.level])) return false;
  if (!hasAny(selected.colors, [card.color])) return false;
  if (selected.ownBands.size) {
    const traits = new Set([...(card.own_traits || []), ...(card.own_bands || [])]);
    if (![...selected.ownBands].some((b) => traits.has(b))) return false;
  }
  if (selected.triggers.size) {
    const keys = (card.filter_triggers || []).map((t) => t.key);
    if (!keys.some((k) => selected.triggers.has(k))) return false;
  }
  if (selected.cxCombo.has("yes") && !card.cx_combo) return false;
  if (selected.searchFrom.size) {
    if (!(card.search_from || []).some((x) => selected.searchFrom.has(x))) return false;
  }
  if (selected.searchWhen.size) {
    const keys = (card.search_when || []).map((w) => w.key);
    if (!keys.some((k) => selected.searchWhen.has(k))) return false;
  }
  if (selected.lookN.size) {
    if (!(card.look_n || []).some((n) => selected.lookN.has(String(n)))) return false;
  }
  if (!matchesTraitFilter(selected.searchTargets, card.search_targets || [], "any_char")) return false;
  if (!matchesTraitFilter(selected.powerKinds, card.power_fx?.kinds || [], "any")) return false;
  const atk = Number(card.power ?? -1);
  if (!Number.isNaN(atk) && atk >= 0) {
    const minEl = document.getElementById("atkMin");
    const maxEl = document.getElementById("atkMax");
    const min = minEl.value === "" ? null : Number(minEl.value);
    const max = maxEl.value === "" ? null : Number(maxEl.value);
    if (min !== null && !Number.isNaN(min) && atk < min) return false;
    if (max !== null && !Number.isNaN(max) && atk > max) return false;
    if (selected.atkBands.size) {
      const ok = [...selected.atkBands].some((band) => {
        if (band === "10000") return atk >= 10000;
        const [a, b] = band.split("-").map(Number);
        return atk >= a && atk <= b;
      });
      if (!ok) return false;
    }
  } else if (selected.atkBands.size || document.getElementById("atkMin").value || document.getElementById("atkMax").value) {
    if (card.type === "キャラ") return false;
  }
  if (selected.backup.size) {
    const b = card.backup;
    const ok = [...selected.backup].every((flag) => {
      if (!b) return false;
      if (flag === "any") return true;
      if (flag === "stock0") return b.stock === 0;
      if (flag === "stock1") return b.stock === 1;
      if (flag === "extra") return b.extra;
      if (flag === "plain") return b && !b.extra;
      return true;
    });
    if (!ok) return false;
  }
  if (selected.backupExtra.size) {
    const kinds = (card.backup?.extra_kinds || []).map((x) => x.key);
    if (!kinds.some((k) => selected.backupExtra.has(k))) return false;
  }
  if (selected.brainstorm.size) {
    const ok = [...selected.brainstorm].every((flag) => {
      if (flag === "yes") return card.brainstorm;
      return (card.brainstorm_payoff || []).includes(flag);
    });
    if (!ok) return false;
  }
  if (selected.mechanics.size) {
    const flags = [];
    if (card.battle_reverse) flags.push("battle_reverse");
    if (card.experience) flags.push("experience");
    if (card.resonate) flags.push("resonate");
    if (![...selected.mechanics].some((k) => flags.includes(k))) return false;
  }
  return true;
}

function tagsFor(card) {
  const tags = [];
  if (card.cx_combo) {
    const trig = (card.cx_combo_triggers || []).map((t) => t.label).join("/");
    tags.push({ text: trig ? `CXコンボ・${trig}` : "CXコンボ", gold: true });
  }
  if (card.climax_trigger) tags.push({ text: `觸發・${card.climax_trigger.label}`, gold: true });
  for (const src of card.search_from || []) {
    const map = { deck: "牌庫檢索", top: "頂牌檢索", waiting: "等待室", clock: "Clock", brainstorm: "集中檢索" };
    tags.push({ text: map[src] || src });
  }
  const when = (card.search_when || []).map((w) => w.label).join("/");
  const look = (card.look_n || []).map((n) => `${n}找`).join("/");
  if (when || look) tags.push({ text: [when, look].filter(Boolean).join("・"), gold: true });
  if ((card.search_targets || []).includes("music")) tags.push({ text: "檢索・音樂" });
  if ((card.search_targets || []).includes("band")) tags.push({ text: `檢索・${(card.search_bands || []).join("/") || "團"}` });
  if ((card.search_targets || []).includes("anniversary")) tags.push({ text: "檢索・周年" });
  if ((card.search_targets || []).includes("any_char")) tags.push({ text: "檢索・不限" });
  if ((card.power_fx?.kinds || []).includes("music")) tags.push({ text: "加攻・音樂" });
  if ((card.power_fx?.kinds || []).includes("band")) tags.push({ text: "加攻・團名" });
  if ((card.power_fx?.kinds || []).includes("anniversary")) tags.push({ text: "加攻・周年" });
  if ((card.power_fx?.kinds || []).includes("any")) tags.push({ text: "加攻・不限" });
  if (card.backup) {
    const extra = card.backup.extra ? "＋效果" : "";
    tags.push({ text: `助太刀 ${card.backup.power ?? "?"} / (${card.backup.stock ?? "?"})${extra}` });
  }
  if (card.brainstorm) tags.push({ text: `集中${card.brainstorm_payoff?.length ? "・" + card.brainstorm_payoff.join("/") : ""}` });
  if (card.battle_reverse) tags.push({ text: "對手倒置" });
  if (card.experience) tags.push({ text: "経験" });
  if (card.resonate) tags.push({ text: "共鳴" });
  return tags;
}

function renderCard(card) {
  const el = document.createElement("article");
  el.className = `card ${card.color || ""}`;
  el.innerHTML = `
    <div class="card-head">
      <div class="card-name">${escapeHtml(card.name)}</div>
      <div class="card-id">${escapeHtml(card.id)}</div>
    </div>
    <div class="stats"><span>Lv${card.level ?? "-"}</span><span>C${card.cost ?? "-"}</span><span class="atk">${escapeHtml(formatPower(card))}</span><span>S${card.soul ?? "-"}</span><span>${card.rare || ""}</span></div>
    <div class="tags">${tagsFor(card).map((t) => `<span class="tag${t.gold ? " gold" : ""}">${escapeHtml(t.text)}</span>`).join("")}</div>
    <div class="excerpt">${escapeHtml(card.text || "")}</div>
  `;
  el.addEventListener("click", () => openDetail(card));
  return el;
}

function openDetail(card) {
  const drawer = document.getElementById("drawer");
  const searchBind = [
    ...(card.search_targets || []).map((t) => ({
      music: "音樂",
      band: "團名 " + (card.search_bands || []).join("/"),
      anniversary: "周年",
      any_char: "不限標籤",
      named: "指定卡名",
      cx: "CX",
    }[t] || t)),
  ].join("、") || "無";
  const powerBind = (card.power_fx?.kinds || []).map((k) => ({
    music: "音樂",
    band: "團名 " + (card.power_fx?.bands || []).join("/"),
    anniversary: "周年",
    any: "不限標籤",
    other: "其他",
  }[k] || k)).join("、") || "無";
  const combo = card.cx_combo
    ? `${(card.cx_combo_names || []).join(" / ") || "有"}　${(card.cx_combo_triggers || []).map((t) => t.label).join(" / ")}`
    : "無";
  document.getElementById("detail").innerHTML = `
    <h2>${escapeHtml(card.name)}</h2>
    <div class="card-id">${escapeHtml(card.id)}　${card.type}　${card.color}　${card.rare || ""}</div>
    <div class="stats"><span>Lv${card.level ?? "-"}</span><span>Cost ${card.cost ?? "-"}</span><span class="atk">${escapeHtml(formatPower(card).replace(/^P/, "Power "))}</span><span>Soul ${card.soul ?? "-"}</span></div>
    <div class="tags">${(card.own_traits || []).map((t) => `<span class="tag">${escapeHtml(t)}</span>`).join("")}</div>
    <div class="kv">CX コンボ：<b>${escapeHtml(combo)}</b></div>
    <div class="kv">檢索綁定：<b>${escapeHtml(searchBind)}</b></div>
    <div class="kv">檢索時機／張數：<b>${escapeHtml([(card.search_when || []).map((w) => w.label).join("、") || "—", (card.look_n || []).map((n) => n + "找").join("、") || "—"].join(" / "))}</b></div>
    <div class="kv">加攻綁定：<b>${escapeHtml(powerBind)}</b></div>
    <div class="kv">效果加攻：<b>${escapeHtml(formatPowerBonus(card))}</b></div>
    <div class="kv">對手倒置：<b>${card.battle_reverse ? "有（バトル相手がリバース）" : "無"}</b></div>
    <div class="kv">助太刀：<b>${card.backup ? `${card.backup.power} / Lv${card.backup.level} / 代價${card.backup.stock}${card.backup.extra ? " / 有額外效果" : ""}` : "無"}</b></div>
    <div class="kv">集中：<b>${card.brainstorm ? (card.brainstorm_payoff.join("、") || "有") : "無"}</b></div>
    <pre class="detail-text">${escapeHtml(card.text || "")}</pre>
  `;
  drawer.classList.remove("hidden");
  drawer.setAttribute("aria-hidden", "false");
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[ch]));
}

function printedPower(card) {
  const n = Number(card.power);
  return Number.isFinite(n) ? n : null;
}

function sortPower(card) {
  const p = printedPower(card);
  if (p === null || p < 0) return -1;
  return p + Number(card.power_fx?.sort_bonus || 0);
}

function formatPower(card) {
  const p = printedPower(card);
  if (p === null) return "P-";
  const bonus = Number(card.power_fx?.sort_bonus || 0);
  if (!bonus) return `P${p}`;
  return `P${p}→${p + bonus}`;
}

function formatPowerBonus(card) {
  const fx = card.power_fx || {};
  const parts = (fx.bonuses || []).map((n) => `+${n}`);
  if (fx.bonus_x) parts.push("+X");
  const sortBonus = Number(fx.sort_bonus || 0);
  if (!parts.length && !sortBonus) return "無";
  const shown = parts.join(" / ") || "無";
  if (sortBonus && (parts.length !== 1 || Number(fx.bonuses?.[0]) !== sortBonus)) {
    return `${shown}　排序估 +${sortBonus}`;
  }
  return shown;
}

function sortValue(card, field) {
  if (field === "power") return sortPower(card);
  if (field === "level" || field === "cost" || field === "soul") return card[field] ?? -1;
  if (field === "color") return COLOR_RANK[card.color] ?? 9;
  if (field === "type") return TYPE_RANK[card.type] ?? 9;
  if (field === "name") return card.name || "";
  if (field === "rare") return card.rare || "";
  return card.id || "";
}

function cmp(a, b, field, dir) {
  if (!field) return 0;
  const av = sortValue(a, field);
  const bv = sortValue(b, field);
  let n = 0;
  if (typeof av === "number" && typeof bv === "number") n = av - bv;
  else n = String(av).localeCompare(String(bv), "ja");
  return dir === "desc" ? -n : n;
}

function apply() {
  const keys = [1, 2, 3].map((n) => ({
    field: document.getElementById(`sort${n}`).value,
    dir: document.getElementById(`dir${n}`).value,
  }));
  const list = cards.filter(matches).sort((a, b) => {
    for (const k of keys) {
      const n = cmp(a, b, k.field, k.dir);
      if (n) return n;
    }
    return 0;
  });
  const unboundNote = includeUnbound() && (selected.searchTargets.size || selected.powerKinds.size)
    ? "　（含不限標籤）"
    : "";
  document.getElementById("count").textContent = `${list.length} / ${cards.length} 張${unboundNote}`;
  refreshFilterToggle();
  const host = document.getElementById("results");
  host.innerHTML = "";
  const frag = document.createDocumentFragment();
  for (const card of list) frag.appendChild(renderCard(card));
  host.appendChild(frag);
}

document.getElementById("q").addEventListener("input", apply);
document.getElementById("includeUnbound").addEventListener("change", apply);
document.getElementById("atkMin").addEventListener("input", apply);
document.getElementById("atkMax").addEventListener("input", apply);
document.getElementById("reset").addEventListener("click", () => {
  for (const set of Object.values(selected)) set.clear();
  document.getElementById("q").value = "";
  document.getElementById("includeUnbound").checked = true;
  document.getElementById("atkMin").value = "";
  document.getElementById("atkMax").value = "";
  for (let n = 1; n <= 3; n++) {
    document.getElementById(`sort${n}`).value = DEFAULT_SORT[n - 1][0];
    document.getElementById(`dir${n}`).value = DEFAULT_SORT[n - 1][1];
  }
  document.querySelectorAll(".chip.on").forEach((el) => el.classList.remove("on"));
  apply();
});
document.getElementById("closeDrawer").addEventListener("click", () => {
  document.getElementById("drawer").classList.add("hidden");
});
document.getElementById("drawer").addEventListener("click", (e) => {
  if (e.target.id === "drawer") e.target.classList.add("hidden");
});

function activeFilterCount() {
  let n = 0;
  for (const set of Object.values(selected)) n += set.size;
  if (document.getElementById("q").value.trim()) n += 1;
  if (document.getElementById("atkMin").value || document.getElementById("atkMax").value) n += 1;
  return n;
}

function refreshFilterToggle() {
  const btn = document.getElementById("filterToggle");
  const n = activeFilterCount();
  btn.textContent = n ? `篩選 ${n}` : "篩選";
  btn.classList.toggle("has-on", n > 0);
}

function setFiltersOpen(open) {
  document.body.classList.toggle("filters-open", open);
  document.getElementById("filterBackdrop").hidden = !open;
  document.getElementById("filterToggle").setAttribute("aria-expanded", open ? "true" : "false");
}

function boot(data) {
  cards = data;
  apply();
}

fillSortSelects();
renderChips();
document.getElementById("filterToggle").addEventListener("click", () => {
  setFiltersOpen(!document.body.classList.contains("filters-open"));
});
document.getElementById("closeFilters").addEventListener("click", () => setFiltersOpen(false));
document.getElementById("filterBackdrop").addEventListener("click", () => setFiltersOpen(false));
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && document.body.classList.contains("filters-open")) setFiltersOpen(false);
});
if (Array.isArray(window.CARDS) && window.CARDS.length) {
  boot(window.CARDS);
} else {
  fetch("cards.json")
    .then((r) => r.json())
    .then(boot)
    .catch((err) => {
      document.getElementById("count").textContent = "載入失敗：" + err;
    });
}
