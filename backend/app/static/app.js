// ===== JackeyFootball 前端（原生 JS，无构建依赖） =====

const POS_ORDER = ["forward", "midfielder", "defender", "goalkeeper"];

const POS_META = {
  forward:    { zh: "前锋", en: "Forward",     color: "#FF5A36" },
  midfielder: { zh: "中场", en: "Midfielder", color: "#1FB6C9" },
  defender:   { zh: "后卫", en: "Defender",   color: "#2ECC71" },
  goalkeeper: { zh: "门将", en: "Goalkeeper", color: "#9B59F6" },
};

const I18N = {
  zh: {
    "nav.power": "综合实力", "nav.data": "各数据", "nav.compare": "球员对比",
    "hero.title": "为你展现最完整的球员数据",
    "hero.sub": "按位置分组 · 综合实力评分 · 同位置内比统治力与巅峰期",
    "pos.all": "全部", "pos.forward": "前锋", "pos.midfielder": "中场",
    "pos.defender": "后卫", "pos.goalkeeper": "门将",
    "loading": "数据加载中…", "empty": "暂无球员数据。",
    "footer": "数据来源参考：StatsBomb / FBref / TheSportsDB 等公开数据，仅供学习研究，非商业用途。",
    "detail.score": "综合实力评分", "detail.stats": "基础数据", "detail.breakdown": "评分维度分解",
    "detail.honors": "团队荣誉", "detail.awards": "个人荣誉", "detail.none": "暂无记录",
    "captain": "队长", "vice": "副队长",
    "scoring.title": "评分怎么算的？",
    "scoring.formula": "综合实力 = 同位置归一化后加权：",
    "scoring.stats": "个人数据能力", "scoring.awards": "个人荣誉", "scoring.honors": "团队荣誉",
    "scoring.market": "身价", "scoring.leader": "领导力",
    "scoring.tip": "所有分值按同位置统一归一化到 0-100 区间。",
  },
  en: {
    "nav.power": "Power", "nav.data": "Stats", "nav.compare": "Compare",
    "hero.title": "The most complete player data, revealed",
    "hero.sub": "Grouped by position · Overall rating · Compare dominance within the same role",
    "pos.all": "All", "pos.forward": "Forward", "pos.midfielder": "Midfield",
    "pos.defender": "Defender", "pos.goalkeeper": "Goalkeeper",
    "loading": "Loading…", "empty": "No player data yet.",
    "footer": "Data sources: StatsBomb / FBref / TheSportsDB and other public datasets. For educational & research purposes only. Non-commercial use.",
    "detail.score": "Overall Rating", "detail.stats": "Key Stats", "detail.breakdown": "Rating Breakdown",
    "detail.honors": "Team Honors", "detail.awards": "Individual Awards", "detail.none": "None",
    "captain": "Captain", "vice": "Vice",
    "scoring.title": "How is the rating calculated?",
    "scoring.formula": "Overall = Normalized (within position) Weighted Score:",
    "scoring.stats": "Statistical Performance", "scoring.awards": "Individual Awards", "scoring.honors": "Team Honors",
    "scoring.market": "Market Value", "scoring.leader": "Leadership",
    "scoring.tip": "All scores are normalized within the same position to a 0-100 scale.",
  },
};

const STAT_LABELS = {
  zh: { season:"赛季", appearances:"出场", minutes_played:"分钟",
    goals:"进球", assists:"助攻", shots_total:"射门", shots_on_target:"射正",
    pass_accuracy:"传球成功率", key_passes:"关键传球", tackles:"抢断",
    interceptions:"拦截", clearances:"解围", blocks:"封堵", saves:"扑救",
    clean_sheets:"零封", goals_conceded:"失球", dribbles_completed:"成功过人",
    aerial_duels_won:"空中对抗", fouls_committed:"犯规", fouls_drawn:"被犯规",
    yellow_cards:"黄牌", red_cards:"红牌" },
  en: { season:"Season", appearances:"Apps", minutes_played:"Mins",
    goals:"Goals", assists:"Assists", shots_total:"Shots", shots_on_target:"On Target",
    pass_accuracy:"Pass %", key_passes:"Key Pass", tackles:"Tackles",
    interceptions:"Intercept", clearances:"Clear", blocks:"Blocks", saves:"Saves",
    clean_sheets:"Clean Sheets", goals_conceded:"Conceded", dribbles_completed:"Dribbles",
    aerial_duels_won:"Aerials", fouls_committed:"Fouls", fouls_drawn:"Fouls Won",
    yellow_cards:"Yellow", red_cards:"Red" },
};

const BD_LABELS = {
  zh: { stats_raw:"个人数据", award_raw:"个人荣誉", honor_raw:"团队荣誉",
    market_value_raw:"身价", leadership_raw:"队长影响力" },
  en: { stats_raw:"Stats", award_raw:"Awards", honor_raw:"Honors",
    market_value_raw:"Market Value", leadership_raw:"Leadership" },
};

let LANG = localStorage.getItem("jf_lang") || "zh";
let ALL_PLAYERS = [];
let ACTIVE_POS = "all";

const $ = (s) => document.querySelector(s);
const t = (k) => (I18N[LANG][k] ?? k);

function applyI18n() {
  document.documentElement.lang = LANG === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.getAttribute("data-i18n"));
  });
  $(".lang-zh").classList.toggle("lang-active", LANG === "zh");
  $(".lang-en").classList.toggle("lang-active", LANG === "en");
}

function initials(name) {
  if (!name) return "?";
  const ascii = /^[A-Za-z\s.]+$/.test(name);
  if (ascii) {
    return name.split(/\s+/).map((w) => w[0]).join("").slice(0, 2).toUpperCase();
  }
  return name.slice(0, 2);
}

function avatarHTML(p) {
  const meta = POS_META[p.position] || { color: "#888" };
  if (p.image_url) {
    return `<img class="avatar" src="${p.image_url}" alt="${p.name}" loading="lazy"
      onerror="this.outerHTML='${avatarFallback(p, meta.color)}'" />`;
  }
  return avatarFallback(p, meta.color);
}

function avatarFallback(p, color) {
  return `<div class="avatar-fallback" style="background:${color}">${initials(p.name)}</div>`;
}

function playerName(p) {
  return LANG === "zh" ? p.name : (p.name_en || p.name);
}

function rowHTML(p, rank) {
  const meta = POS_META[p.position] || { color: "#888" };
  const score = (p.overall_score ?? 0).toFixed(1);
  const captain = p.is_captain
    ? `<span class="captain-badge">${t("captain")}</span>`
    : (p.is_vice_captain ? `<span class="captain-badge">${t("vice")}</span>` : "");
  const mv = p.market_value_euro
    ? "€" + (p.market_value_euro >= 1e6
        ? (p.market_value_euro / 1e6).toFixed(1) + "M"
        : (p.market_value_euro / 1e3).toFixed(0) + "K")
    : "";
  return `
    <div class="player-row" data-id="${p.id}">
      <div class="rank ${rank <= 3 ? "top" : ""}">${rank}</div>
      ${avatarHTML(p)}
      <div class="pinfo">
        <div class="pname">${playerName(p)}${captain}</div>
        <div class="pmeta">${p.current_club}<span class="sep">·</span>${p.club_league}<span class="sep">·</span>${p.age}岁</div>
      </div>
      <div class="pmeta" style="text-align:right;color:var(--text-1);font-size:13px">
        ${p.nationality}<br/>${mv}
      </div>
      <div class="score-col">
        <div class="score-num" style="color:${meta.color}">${score}</div>
        <div class="score-bar"><div class="score-fill" style="width:${score}%;background:linear-gradient(90deg,${meta.color},#FFC53D)"></div></div>
      </div>
    </div>`;
}

function renderList() {
  const wrap = $("#listWrap");
  if (!ALL_PLAYERS.length) {
    wrap.innerHTML = `<div class="empty">${t("empty")}</div>`;
    return;
  }
  if (ACTIVE_POS === "all") {
    let html = "";
    for (const pos of POS_ORDER) {
      const group = ALL_PLAYERS.filter((p) => p.position === pos);
      if (!group.length) continue;
      const meta = POS_META[pos];
      html += `<section class="pos-section">
        <div class="pos-head" style="color:${meta.color}">
          <span class="pos-dot" style="background:${meta.color};color:${meta.color}"></span>
          ${meta[LANG]} <span style="color:var(--text-1);font-weight:500;font-size:14px">(${group.length})</span>
        </div>`;
      group.forEach((p, i) => { html += rowHTML(p, i + 1); });
      html += `</section>`;
    }
    wrap.innerHTML = html;
  } else {
    const group = ALL_PLAYERS.filter((p) => p.position === ACTIVE_POS);
    wrap.innerHTML = group.map((p, i) => rowHTML(p, i + 1)).join("");
  }
  wrap.querySelectorAll(".player-row").forEach((row) => {
    row.addEventListener("click", () => openDetail(row.getAttribute("data-id")));
  });
}

async function openDetail(id) {
  const body = $("#drawerBody");
  body.innerHTML = `<div class="loading">${t("loading")}</div>`;
  $("#drawer").classList.add("open");
  $("#drawerMask").classList.add("open");
  try {
    const res = await fetch(`/api/players/${id}`);
    if (!res.ok) throw new Error("not found");
    const p = await res.json();
    body.innerHTML = detailHTML(p);
  } catch (e) {
    body.innerHTML = `<div class="empty">${t("empty")}</div>`;
  }
}

function detailHTML(p) {
  const meta = POS_META[p.position] || { color: "#888", [LANG]: p.position };
  const score = (p.overall_score ?? 0).toFixed(1);
  const name = playerName(p);

  // 基础数据
  let statsHTML = "";
  if (p.stats) {
    const lbl = STAT_LABELS[LANG];
    for (const [k, v] of Object.entries(p.stats)) {
      if (k === "id" || k === "player_id" || v == null || v === "") continue;
      const txt = k === "pass_accuracy" ? (v + "%") : v;
      statsHTML += `<div class="stat-cell"><div class="k">${lbl[k] || k}</div><div class="v">${txt}</div></div>`;
    }
  }
  if (!statsHTML) statsHTML = `<div class="empty" style="padding:10px">${t("detail.none")}</div>`;

  // 评分维度分解
  let bdHTML = "";
  if (p.score_breakdown) {
    const lbl = BD_LABELS[LANG];
    for (const [k, v] of Object.entries(p.score_breakdown)) {
      bdHTML += `<div class="bd-row">
        <div class="bd-top"><span>${lbl[k] || k}</span><span>${v}</span></div>
        <div class="bd-bar"><div class="bd-fill" style="width:${v}%"></div></div>
      </div>`;
    }
  }

  // 荣誉 / 奖项
  const honors = (p.honors || []).map((h) =>
    `<span class="tag">${h.honor_name} ×${h.count}${h.year ? " · " + h.year : ""}</span>`).join("") || `<span class="empty" style="padding:6px">${t("detail.none")}</span>`;
  const awards = (p.awards || []).map((a) =>
    `<span class="tag">${a.award_name} ×${a.count}${a.year ? " · " + a.year : ""}</span>`).join("") || `<span class="empty" style="padding:6px">${t("detail.none")}</span>`;

  return `
    <div class="d-head">
      ${avatarHTML(p)}
      <div>
        <div class="pname">${name}</div>
        <div class="pmeta">${meta[LANG]} · ${p.current_club} · ${p.national_team}</div>
      </div>
    </div>
    <div class="d-score">
      <div class="big">${score}</div>
      <div class="lbl">${t("detail.score")}</div>
    </div>
    <div class="section-title">${t("detail.stats")}</div>
    <div class="stat-grid">${statsHTML}</div>
    <div class="section-title">${t("detail.breakdown")}</div>
    ${bdHTML}
    <div class="section-title">${t("detail.honors")}</div>
    <div>${honors}</div>
    <div class="section-title">${t("detail.awards")}</div>
    <div>${awards}</div>`;
}

function closeDrawer() {
  $("#drawer").classList.remove("open");
  $("#drawerMask").classList.remove("open");
}

async function init() {
  applyI18n();
  try {
    const res = await fetch("/api/players");
    ALL_PLAYERS = await res.json();
  } catch (e) {
    ALL_PLAYERS = [];
  }
  renderList();

  // 筛选
  $("#filters").addEventListener("click", (e) => {
    const btn = e.target.closest(".chip");
    if (!btn) return;
    document.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
    btn.classList.add("active");
    ACTIVE_POS = btn.getAttribute("data-pos");
    renderList();
  });

  // 语言切换
  $("#langToggle").addEventListener("click", () => {
    LANG = LANG === "zh" ? "en" : "zh";
    localStorage.setItem("jf_lang", LANG);
    applyI18n();
    renderList();
  });

  // 抽屉关闭
  $("#drawerClose").addEventListener("click", closeDrawer);
  $("#drawerMask").addEventListener("click", closeDrawer);
}

init();
