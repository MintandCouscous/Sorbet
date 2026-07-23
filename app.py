"""Sorbet — M&A Mapping Wizard · Accomplir Advisors"""

import contextlib, io, os, tempfile, time as _time
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
from automap import (
    MOTIVATIONS, COMPANY_TYPES, COUNT_OPTIONS,
    generate_strategy, discover_companies, enrich_all, generate_excel,
    reset_cost, get_cost_summary,
)

st.set_page_config(page_title="Sorbet · Accomplir", page_icon="🍧", layout="wide")

# ── Constants ─────────────────────────────────────────────────────────────────
STEP_NAMES  = ["The Deal", "The Market", "Motivations", "Volume", "Run"]
STEP_ICONS  = ["🍓", "🍋", "🌿", "🍊", "🍧"]
STEP_COLORS = ["#E8305A", "#B89000", "#0A9E80", "#D04818", "#8B1A42"]
N_STEPS     = 5
DEFAULT_CAP = 15

SORBET_SVG = """<svg viewBox="0 0 300 460" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="shine" cx="28%" cy="22%" r="55%"><stop offset="0%" stop-color="#fff" stop-opacity=".72"/><stop offset="100%" stop-color="#fff" stop-opacity="0"/></radialGradient>
    <radialGradient id="g-str" cx="35%" cy="28%" r="65%"><stop offset="0%" stop-color="#FFB3CB"/><stop offset="45%" stop-color="#FF4D7D"/><stop offset="100%" stop-color="#B80044"/></radialGradient>
    <radialGradient id="g-lem" cx="35%" cy="28%" r="65%"><stop offset="0%" stop-color="#FFFAAA"/><stop offset="45%" stop-color="#FFE234"/><stop offset="100%" stop-color="#BF9800"/></radialGradient>
    <radialGradient id="g-mnt" cx="35%" cy="28%" r="65%"><stop offset="0%" stop-color="#B8F4E8"/><stop offset="45%" stop-color="#3DD9B5"/><stop offset="100%" stop-color="#0A9E80"/></radialGradient>
    <linearGradient id="cone-g" x1="20%" y1="0%" x2="80%" y2="100%"><stop offset="0%" stop-color="#E8B030"/><stop offset="100%" stop-color="#8B5000"/></linearGradient>
    <clipPath id="cone-clip"><polygon points="62,262 238,262 150,445"/></clipPath>
  </defs>
  <ellipse cx="150" cy="453" rx="72" ry="8" fill="#CCA878" opacity=".4"/>
  <polygon points="62,262 238,262 150,445" fill="url(#cone-g)"/>
  <g clip-path="url(#cone-clip)" stroke="#6B3800" stroke-width="1.2" opacity=".35">
    <line x1="48" y1="248" x2="178" y2="455"/><line x1="84" y1="248" x2="210" y2="448"/><line x1="120" y1="248" x2="238" y2="440"/><line x1="156" y1="248" x2="258" y2="420"/>
    <line x1="252" y1="248" x2="124" y2="456"/><line x1="224" y1="248" x2="98" y2="452"/><line x1="196" y1="248" x2="74" y2="446"/>
    <line x1="62" y1="262" x2="238" y2="262"/><line x1="82" y1="300" x2="220" y2="300"/><line x1="100" y1="338" x2="202" y2="338"/><line x1="118" y1="374" x2="184" y2="374"/>
  </g>
  <ellipse cx="150" cy="262" rx="88" ry="12" fill="url(#cone-g)"/>
  <ellipse cx="150" cy="262" rx="88" ry="12" fill="#fff" opacity=".2"/>
  <circle cx="150" cy="226" r="86" fill="url(#g-str)"/><circle cx="150" cy="226" r="86" fill="url(#shine)"/>
  <path d="M118,306 Q112,326 110,340 Q108,350 114,351 Q120,352 122,342 Q124,330 124,310" fill="#FF4D7D" opacity=".85"/>
  <path d="M182,304 Q188,322 186,334 Q184,344 179,343 Q174,342 176,332 Q178,320 180,306" fill="#B80044" opacity=".75"/>
  <circle cx="143" cy="144" r="76" fill="url(#g-lem)"/><circle cx="143" cy="144" r="76" fill="url(#shine)"/>
  <path d="M112,216 Q106,232 104,244 Q102,254 108,255 Q114,256 116,245 Q118,233 116,218" fill="#FFE234" opacity=".85"/>
  <circle cx="156" cy="72" r="66" fill="url(#g-mnt)"/><circle cx="156" cy="72" r="66" fill="url(#shine)"/>
  <g transform="translate(214,16) rotate(18)"><path d="M0,-13 Q9,-7 11,2 Q7,15 0,21 Q-7,15 -11,2 Q-9,-7 0,-13Z" fill="#E01848"/>
    <path d="M-2,-15 Q0,-9 2,-15" stroke="#5A9E20" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <ellipse cx="-1" cy="2" rx="1.4" ry="2" fill="#FFB3C0" transform="rotate(-10 -1 2)"/>
    <ellipse cx="4" cy="-3" rx="1.4" ry="2" fill="#FFB3C0" transform="rotate(15 4 -3)"/>
  </g>
  <g transform="translate(96,22) rotate(-38)"><path d="M0,0 Q9,-17 0,-30 Q-9,-17 0,0Z" fill="#2DC8A0"/><line x1="0" y1="0" x2="0" y2="-30" stroke="#1A9070" stroke-width="1.2" opacity=".6"/></g>
  <g transform="translate(84,12) rotate(-58)"><path d="M0,0 Q6,-12 0,-22 Q-6,-12 0,0Z" fill="#3DD9B5" opacity=".85"/></g>
  <g transform="translate(40,114)"><circle r="17" fill="#FFE234" stroke="#BF9800" stroke-width="1.5"/><circle r="8.5" fill="#FFFAAA"/>
    <line x1="-17" y1="0" x2="17" y2="0" stroke="#BF9800" stroke-width=".8" opacity=".5"/>
    <line x1="0" y1="-17" x2="0" y2="17" stroke="#BF9800" stroke-width=".8" opacity=".5"/>
    <line x1="-12" y1="-12" x2="12" y2="12" stroke="#BF9800" stroke-width=".8" opacity=".5"/>
    <line x1="12" y1="-12" x2="-12" y2="12" stroke="#BF9800" stroke-width=".8" opacity=".5"/>
  </g>
  <text x="266" y="68" font-size="15" fill="#FF4D7D" style="animation:sp 3.2s ease-in-out infinite">&#x2726;</text>
  <text x="22" y="172" font-size="11" fill="#FFE234" style="animation:sp 3.2s ease-in-out 1.1s infinite">&#x2726;</text>
  <text x="272" y="188" font-size="9" fill="#3DD9B5" style="animation:sp 3.2s ease-in-out 2.2s infinite">&#x2726;</text>
  <text x="34" y="84" font-size="13" fill="#FF4D7D" style="animation:sp 3.2s ease-in-out .6s infinite">&#x2726;</text>
</svg>"""

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("step", 1), ("strategy", None), ("log_lines", []),
             ("excel_bytes", None), ("excel_filename", ""), ("run_triggered", False),
             ("_form", {}), ("_per_cat_caps", {})]:
    if k not in st.session_state:
        st.session_state[k] = v

step  = st.session_state.step
color = STEP_COLORS[min(step - 1, N_STEPS - 1)]

# ── Helpers ───────────────────────────────────────────────────────────────────
def _save_form(**kwargs):
    """Persist form values to non-widget state so they survive step transitions."""
    st.session_state["_form"].update(kwargs)

def _build_inp():
    """Read from persistent _form dict — never from widget state (which gets cleared)."""
    f = st.session_state["_form"]
    return {
        "is_sellside":       f.get("mandate", "Sell-side") == "Sell-side",
        "client":            f.get("client", ""),
        "company_desc":      f.get("desc", ""),
        "sector":            f.get("sector", ""),
        "sub_sector":        f.get("sub", ""),
        "geography":         f.get("geo", ""),
        "target_geography":  f.get("tgeo", "") or "Pan-India",
        "motivations":       list(f.get("motivations") or []),
        "company_types":     list(f.get("types") or COMPANY_TYPES),
        "revenue_range":     f.get("revenue", "") or "No filter",
        "specific_attrs":    f.get("attrs", "") or "None",
        "what_looking_for":  f.get("seeking", "") or "None",
        "exclude_companies": f.get("exclude", ""),
        "per_cat_cap":       DEFAULT_CAP,
        "date":              datetime.today().strftime("%d-%b-%y"),
    }

def _colorize(line: str) -> str:
    s = line.rstrip()
    if not s.strip(): return "<br>"
    esc = s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    if "━" in s: return f'<span style="color:{color};opacity:.4">{esc}</span>'
    if s.lstrip().startswith("[") and "/4]" in s: return f'<span style="color:#FFB3CB;font-weight:700">{esc}</span>'
    if "[ERROR]" in s: return f'<span style="color:#FF6B8A">{esc}</span>'
    if "✓" in s or "DONE" in s: return f'<span style="color:#fff">{esc}</span>'
    if "↳" in s: return f'<span style="color:#9B7A8E">{esc}</span>'
    return f'<span style="color:#C49AAE">{esc}</span>'

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@1,9..144,300..700&family=Inter:wght@300;400;500;600;700&display=swap');
@keyframes sp {{ 0%,100%{{opacity:.15;transform:scale(.6) rotate(0deg)}} 50%{{opacity:1;transform:scale(1.3) rotate(20deg)}} }}
@keyframes floatArt {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-12px)}} }}
@keyframes stepIn {{ from{{opacity:0;transform:translateY(18px)}} to{{opacity:1;transform:translateY(0)}} }}
@keyframes pulse {{ 0%,100%{{opacity:.5}} 50%{{opacity:1}} }}

:root {{ --clr:{color}; }}
*,html,body,[class*="css"] {{ font-family:'Inter',sans-serif !important; box-sizing:border-box; }}

/* ─ Full bleed ─ */
.stApp {{
  background:#FFF5F8 !important;
  background-image:
    radial-gradient(ellipse 70% 50% at 15% 5%, {color}0D 0%,transparent 100%),
    radial-gradient(ellipse 60% 50% at 85% 95%, #3DD9B50C 0%,transparent 100%) !important;
}}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {{ display:none !important; }}
section[data-testid="stMain"] > div:first-child {{ padding-top:0 !important; }}
.block-container {{ padding:0 3rem 3rem !important; max-width:100% !important; }}

/* ─ Sticky nav ─ */
.snav {{
  position:sticky; top:0; z-index:999;
  display:flex; align-items:center; justify-content:space-between;
  padding:16px 0 14px; margin-bottom:32px;
  border-bottom:1px solid #FFE4EC;
  background:rgba(255,245,248,.88); backdrop-filter:blur(18px);
}}
.snav-logo {{
  font-family:'Fraunces',serif; font-style:italic; font-size:22px;
  color:#8B1A42; letter-spacing:-.01em;
}}
.snav-steps {{ display:flex; align-items:center; gap:2px; }}
.snav-step {{
  font-size:10px; font-weight:600; letter-spacing:.1em; text-transform:uppercase;
  padding:6px 13px; border-radius:20px; color:#C0A8B0;
  display:flex; align-items:center; gap:4px; white-space:nowrap;
}}
.snav-step.done  {{ color:var(--clr); background:color-mix(in srgb,var(--clr) 10%,#fff); }}
.snav-step.active {{
  color:#fff; background:var(--clr);
  box-shadow:0 4px 16px color-mix(in srgb,var(--clr) 38%,transparent);
}}
.snav-sep {{ color:#DDD; font-size:10px; padding:0 1px; }}
.snav-by {{ font-size:10px; font-weight:700; letter-spacing:.18em; text-transform:uppercase; color:#C0A8B0; }}

/* ─ Step layout ─ */
.step-enter {{ animation:stepIn .32s cubic-bezier(.22,.68,0,1.2) both; }}
.step-label {{
  font-size:10px; font-weight:700; letter-spacing:.2em; text-transform:uppercase;
  color:var(--clr); opacity:.7; margin-bottom:8px;
}}
.step-title {{
  font-family:'Fraunces',serif; font-style:italic;
  font-size:clamp(38px,4vw,60px); font-weight:400; line-height:1.0;
  letter-spacing:-.025em; color:#1C1412; margin-bottom:24px;
}}
.step-title em {{ color:var(--clr); font-style:inherit; }}
.step-hint {{ font-size:14px; color:#9B7080; line-height:1.65; margin-bottom:28px; max-width:440px; }}
.art-wrap {{
  display:flex; justify-content:center; align-items:flex-start; padding-top:8px;
  animation:floatArt 5s ease-in-out infinite;
  filter:drop-shadow(0 24px 48px color-mix(in srgb,{color} 22%,transparent));
}}

/* ─ Inputs ─ */
.stTextInput>div>div>input,.stTextArea>div>div>textarea {{
  background:#fff !important; border:1.5px solid #EDD8E2 !important;
  border-radius:12px !important; color:#1C1412 !important;
  font-size:14px !important; padding:12px 16px !important;
  transition:border-color .15s,box-shadow .15s !important;
  box-shadow:0 1px 4px rgba(0,0,0,.04) !important;
}}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus {{
  border-color:var(--clr) !important;
  box-shadow:0 0 0 3px color-mix(in srgb,var(--clr) 12%,transparent) !important; outline:none !important;
}}
.stTextInput>div>div>input::placeholder,.stTextArea>div>div>textarea::placeholder {{ color:#CCAABB !important; }}
.stTextInput label,.stTextArea label {{
  color:#8B5060 !important; font-size:11px !important;
  font-weight:700 !important; letter-spacing:.06em !important; text-transform:uppercase !important;
}}
.stNumberInput input {{
  background:#fff !important; border:1.5px solid #EDD8E2 !important;
  border-radius:10px !important; color:#1C1412 !important; font-size:20px !important;
  font-weight:700 !important; text-align:center !important;
  box-shadow:0 1px 4px rgba(0,0,0,.04) !important;
}}
.stNumberInput input:focus {{ border-color:var(--clr) !important; }}
.stNumberInput label {{ color:#8B5060 !important; font-size:10px !important; font-weight:700 !important; letter-spacing:.06em !important; text-transform:uppercase !important; }}
div[data-testid="stRadioGroup"] label span {{ color:#1C1412 !important; font-size:14px !important; font-weight:500 !important; }}
div[data-testid="stRadioGroup"]>label {{ color:#8B5060 !important; font-size:11px !important; font-weight:700 !important; letter-spacing:.06em !important; text-transform:uppercase !important; }}

/* ─ Pills ─ */
div[data-testid="stPillsGroup"] button {{
  border-radius:24px !important; font-size:13px !important; font-weight:500 !important;
  border:1.5px solid #EDD8E2 !important; color:#6B4055 !important; background:#fff !important;
  padding:7px 16px !important; transition:all .14s !important;
  box-shadow:0 1px 3px rgba(0,0,0,.05) !important;
}}
div[data-testid="stPillsGroup"] button[aria-pressed="true"] {{
  background:var(--clr) !important; color:#fff !important; border-color:var(--clr) !important;
  box-shadow:0 4px 14px color-mix(in srgb,var(--clr) 35%,transparent) !important;
}}
div[data-testid="stPillsGroup"]>label {{
  color:#8B5060 !important; font-size:11px !important; font-weight:700 !important;
  letter-spacing:.06em !important; text-transform:uppercase !important;
}}

/* ─ Category cards ─ */
[data-testid="stVerticalBlockBorderWrapper"] {{
  border-color:color-mix(in srgb,var(--clr) 18%,#fff) !important;
  border-radius:18px !important; background:#fff !important;
  padding:22px 24px 24px !important;
  box-shadow:0 2px 20px rgba(0,0,0,.05) !important;
  transition:box-shadow .22s,transform .22s !important;
}}
[data-testid="stVerticalBlockBorderWrapper"]:hover {{
  box-shadow:0 8px 30px color-mix(in srgb,var(--clr) 14%,rgba(0,0,0,.06)) !important;
  transform:translateY(-2px) !important;
}}
.cat-name {{ font-size:16px; font-weight:700; color:#1C1412; line-height:1.3; margin-bottom:2px; }}

/* ─ Buttons ─ */
div[data-testid="stButton"]>button[kind="primary"] {{
  background:linear-gradient(135deg,var(--clr) 0%,color-mix(in srgb,var(--clr) 68%,#000) 100%) !important;
  color:#fff !important; border:none !important; border-radius:14px !important;
  font-family:'Fraunces',serif !important; font-style:italic !important;
  font-size:20px !important; font-weight:400 !important;
  padding:18px 36px !important; width:100% !important;
  box-shadow:0 8px 28px color-mix(in srgb,var(--clr) 30%,transparent) !important;
  transition:opacity .15s,transform .12s,box-shadow .15s !important;
  letter-spacing:-.01em !important;
}}
div[data-testid="stButton"]>button[kind="primary"]:hover {{
  opacity:.92 !important; transform:translateY(-2px) !important;
  box-shadow:0 14px 36px color-mix(in srgb,var(--clr) 38%,transparent) !important;
}}
div[data-testid="stButton"]>button[kind="primary"]:active {{ transform:translateY(0) !important; opacity:1 !important; }}
div[data-testid="stButton"]>button[kind="secondary"] {{
  background:#fff !important; color:#8B5060 !important;
  border:1.5px solid #EDD8E2 !important; border-radius:12px !important;
  font-size:14px !important; padding:14px 28px !important; width:100% !important;
  transition:background .14s,border-color .14s !important;
}}
div[data-testid="stButton"]>button[kind="secondary"]:hover {{
  background:#FFF5F8 !important; border-color:var(--clr) !important;
}}
div[data-testid="stDownloadButton"]>button {{
  background:linear-gradient(135deg,var(--clr) 0%,color-mix(in srgb,var(--clr) 68%,#000) 100%) !important;
  color:#fff !important; border:none !important; border-radius:14px !important;
  font-family:'Fraunces',serif !important; font-style:italic !important;
  font-size:20px !important; padding:18px 36px !important; width:100% !important; margin-top:10px !important;
  box-shadow:0 8px 28px color-mix(in srgb,var(--clr) 30%,transparent) !important;
}}

/* ─ Log ─ */
.log-box {{
  background:#130810; border:1px solid color-mix(in srgb,{color} 18%,transparent);
  border-radius:18px; padding:22px 26px; font-family:'JetBrains Mono','Fira Code',monospace; font-size:11px;
  line-height:1.95; height:480px; overflow-y:auto; white-space:pre-wrap; word-break:break-word;
}}
.log-box::-webkit-scrollbar {{ width:3px; }}
.log-box::-webkit-scrollbar-thumb {{ background:color-mix(in srgb,var(--clr) 60%,transparent); border-radius:2px; }}

/* ─ Stat tiles ─ */
.stat-tile {{
  background:#fff; border:1px solid #EDD8E2; border-radius:14px;
  padding:16px 18px; text-align:center;
  box-shadow:0 2px 12px rgba(0,0,0,.04);
}}
.stat-val {{ font-family:'Fraunces',serif; font-style:italic; font-size:32px; color:var(--clr); font-weight:400; line-height:1; }}
.stat-label {{ font-size:10px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:#9B7080; margin-top:6px; }}

/* ─ Error banner ─ */
.err-banner {{
  background:#2D0A14; border:1px solid #FF4D7D; border-radius:14px;
  padding:14px 18px; margin:12px 0; color:#FF6B8A; font-size:13px;
  font-family:monospace; line-height:1.6;
}}

/* ─ Progress strip ─ */
.prog-strip {{ background:#EDD8E2; border-radius:99px; height:5px; margin:6px 0 14px; overflow:hidden; }}
.prog-fill {{
  background:linear-gradient(90deg,var(--clr),color-mix(in srgb,var(--clr) 70%,#FF9F00));
  border-radius:99px; height:5px; transition:width .5s ease;
}}
</style>""", unsafe_allow_html=True)

# ── Header nav ────────────────────────────────────────────────────────────────
def _step_cls(i: int) -> str:
    if i + 1 < step:  return "done"
    if i + 1 == step: return "active"
    return ""

steps_html = "".join(
    f'<span class="snav-step {_step_cls(i)}">{STEP_ICONS[i]} {STEP_NAMES[i]}</span>'
    + ('' if i == N_STEPS - 1 else '<span class="snav-sep">›</span>')
    for i in range(N_STEPS)
)
st.markdown(f"""<div class="snav">
  <div class="snav-logo">🍧 Sorbet</div>
  <div class="snav-steps">{steps_html}</div>
  <div class="snav-by">Accomplir Advisors</div>
</div>""", unsafe_allow_html=True)

# ── Step 1 — The Deal ─────────────────────────────────────────────────────────
if step == 1:
    col_form, col_art = st.columns([3, 2], gap="large")

    with col_form:
        st.markdown('<div class="step-enter">', unsafe_allow_html=True)
        st.markdown(f'<div class="step-label">Step 1 of {N_STEPS}</div>', unsafe_allow_html=True)
        st.markdown('<div class="step-title">The <em>Deal</em></div>', unsafe_allow_html=True)
        st.markdown('<div class="step-hint">Tell us about the mandate and who you\'re representing.</div>', unsafe_allow_html=True)
        _f1 = st.session_state["_form"]
        _mandate_opts = ["Sell-side", "Buy-side"]
        _mandate_idx  = _mandate_opts.index(_f1["mandate"]) if _f1.get("mandate") in _mandate_opts else 0
        st.radio("Mandate type", _mandate_opts, horizontal=True, key="s1_mandate", index=_mandate_idx)
        st.text_input("Client company", placeholder="e.g. Cessna Lifeline Ltd.", key="s1_client", value=_f1.get("client",""))
        is_sell = st.session_state.get("s1_mandate", "Sell-side") == "Sell-side"
        st.text_area(
            f"Describe the {'company being sold' if is_sell else 'acquirer'}",
            placeholder="Products & services, revenue size, key markets, deal rationale — paste any doc",
            height=130, key="s1_desc", value=_f1.get("desc",""),
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_art:
        st.markdown(f'<div class="art-wrap">{SORBET_SVG}</div>', unsafe_allow_html=True)

    _, _, next_col = st.columns([1, 3, 1])
    if next_col.button("Continue →", key="n1", type="primary"):
        errs = []
        _client = st.session_state.get("s1_client", "").strip()
        _desc   = st.session_state.get("s1_desc", "").strip()
        if not _client: errs.append("Enter the client company name.")
        if not _desc:   errs.append("Describe the company.")
        if errs:
            for e in errs: st.error(e)
        else:
            _save_form(mandate=st.session_state.get("s1_mandate","Sell-side"), client=_client, desc=_desc)
            st.session_state.strategy = None
            st.session_state.step = 2; st.rerun()

# ── Step 2 — The Market ───────────────────────────────────────────────────────
elif step == 2:
    col_form, col_art = st.columns([3, 2], gap="large")

    with col_form:
        st.markdown('<div class="step-enter">', unsafe_allow_html=True)
        st.markdown(f'<div class="step-label">Step 2 of {N_STEPS}</div>', unsafe_allow_html=True)
        st.markdown('<div class="step-title">The <em>Market</em></div>', unsafe_allow_html=True)
        st.markdown('<div class="step-hint">Define the sector and where to look.</div>', unsafe_allow_html=True)
        _f2 = st.session_state["_form"]
        st.text_input("Sector",      placeholder="e.g. Healthcare Services",  key="s2_sector", value=_f2.get("sector",""))
        st.text_input("Sub-sector",  placeholder="e.g. Veterinary Care",      key="s2_sub",    value=_f2.get("sub",""))
        st.text_input("Client HQ",   placeholder="e.g. Bengaluru, Karnataka", key="s2_geo",    value=_f2.get("geo",""))
        st.text_input("Target geography", placeholder="Pan-India  /  South-East Asia", key="s2_tgeo", value=_f2.get("tgeo",""))
        st.markdown('</div>', unsafe_allow_html=True)

    with col_art:
        st.markdown(f'<div class="art-wrap">{SORBET_SVG}</div>', unsafe_allow_html=True)

    back_col, _, next_col = st.columns([1, 3, 1])
    if back_col.button("← Back", key="b2", type="secondary"):
        st.session_state.step = 1; st.rerun()
    if next_col.button("Continue →", key="n2", type="primary"):
        errs = []
        _sector = st.session_state.get("s2_sector","").strip()
        _sub    = st.session_state.get("s2_sub","").strip()
        _geo    = st.session_state.get("s2_geo","").strip()
        if not _sector: errs.append("Sector is required.")
        if not _sub:    errs.append("Sub-sector is required.")
        if not _geo:    errs.append("Client HQ is required.")
        if errs:
            for e in errs: st.error(e)
        else:
            _save_form(sector=_sector, sub=_sub, geo=_geo, tgeo=st.session_state.get("s2_tgeo",""))
            st.session_state.strategy = None
            st.session_state.step = 3; st.rerun()

# ── Step 3 — Motivations & Filters ───────────────────────────────────────────
elif step == 3:
    col_form, col_art = st.columns([3, 2], gap="large")

    with col_form:
        st.markdown('<div class="step-enter">', unsafe_allow_html=True)
        st.markdown(f'<div class="step-label">Step 3 of {N_STEPS}</div>', unsafe_allow_html=True)
        st.markdown('<div class="step-title"><em>Motivations</em> & Filters</div>', unsafe_allow_html=True)
        st.markdown('<div class="step-hint">Why is this deal happening? What must the target have?</div>', unsafe_allow_html=True)

        _f3 = st.session_state["_form"]
        try:
            st.pills("M&A Motivations — pick all that apply", MOTIVATIONS,
                     default=_f3.get("motivations",[]), selection_mode="multi", key="s3_motivations")
        except AttributeError:
            motiv = []
            for i, m in enumerate(MOTIVATIONS):
                if st.checkbox(m, value=(m in _f3.get("motivations",[])), key=f"s3_m_{i}"): motiv.append(m)
            st.session_state["s3_motivations"] = motiv

        st.text_input("Revenue range",    placeholder=">100 Cr  /  50–500 Cr",     key="s3_revenue", value=_f3.get("revenue",""))
        st.text_input("Must-have attributes", placeholder="PLI recipient / CRISIL rated", key="s3_attrs", value=_f3.get("attrs",""))
        st.text_input("What are you seeking?", placeholder="East India presence / R&D capabilities", key="s3_seeking", value=_f3.get("seeking",""))

        try:
            st.pills("Company types to include", COMPANY_TYPES,
                     default=_f3.get("types", COMPANY_TYPES), selection_mode="multi", key="s3_types")
        except AttributeError:
            types = []
            for i, t in enumerate(COMPANY_TYPES):
                if st.checkbox(t, value=(t in _f3.get("types", COMPANY_TYPES)), key=f"s3_t_{i}"): types.append(t)
            st.session_state["s3_types"] = types

        st.markdown('</div>', unsafe_allow_html=True)

    with col_art:
        st.markdown(f'<div class="art-wrap">{SORBET_SVG}</div>', unsafe_allow_html=True)

    back_col, _, next_col = st.columns([1, 3, 1])
    if back_col.button("← Back", key="b3", type="secondary"):
        st.session_state.step = 2; st.rerun()
    if next_col.button("Continue →", key="n3", type="primary"):
        motivations = list(st.session_state.get("s3_motivations") or [])
        types       = list(st.session_state.get("s3_types") or [])
        errs = []
        if not motivations: errs.append("Select at least one M&A motivation.")
        if not types:       errs.append("Select at least one company type.")
        if errs:
            for e in errs: st.error(e)
        else:
            _save_form(
                motivations=motivations,
                types=types,
                revenue=st.session_state.get("s3_revenue",""),
                attrs=st.session_state.get("s3_attrs",""),
                seeking=st.session_state.get("s3_seeking",""),
            )
            st.session_state.strategy = None
            st.session_state.step = 4; st.rerun()

# ── Step 4 — Volume & Categories ─────────────────────────────────────────────
elif step == 4:
    st.markdown('<div class="step-enter">', unsafe_allow_html=True)
    st.markdown(f'<div class="step-label">Step 4 of {N_STEPS}</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-title">Set <em>Volume</em> per Category</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-hint">We\'ve generated the mapping categories from your inputs. Set how many companies to find in each — click any card for the rationale.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    inp = _build_inp()

    # Auto-generate strategy on first arrival
    if st.session_state.strategy is None:
        with st.spinner("Generating mapping categories from your deal details…"):
            class _Q(io.StringIO):
                def write(self, s): return super().write(s)
            with contextlib.redirect_stdout(_Q()):
                st.session_state.strategy = generate_strategy(inp)
        st.rerun()

    strategy = st.session_state.strategy
    cats     = strategy.get("categories", [])

    regen_col, _ = st.columns([1, 5])
    if regen_col.button("↺ Regenerate", key="regen", type="secondary"):
        st.session_state.strategy = None; st.rerun()

    # Category cards — 2-column grid at top level (safe, no parent column)
    cat_cols = st.columns(2, gap="medium")
    for i, cat in enumerate(cats):
        with cat_cols[i % 2]:
            with st.container(border=True):
                st.markdown(f'<div class="cat-name">{STEP_ICONS[2]} {cat["name"]}</div>', unsafe_allow_html=True)
                st.number_input("Companies to find", min_value=1, max_value=250,
                                value=DEFAULT_CAP, step=1, key=f"cat_{i}")
                rationale_text = cat.get("rationale") or cat.get("description") or ""
                if rationale_text:
                    st.caption(rationale_text)

    st.markdown("<br>", unsafe_allow_html=True)
    st.text_area("Already mapped — skip these companies",
                 placeholder="One per line or comma-separated", height=70, key="s4_exclude")

    back_col, _, run_col = st.columns([1, 3, 1])
    if back_col.button("← Back", key="b4", type="secondary"):
        st.session_state.strategy = None
        st.session_state.step = 3; st.rerun()
    if run_col.button("Run Mapping →", key="run_btn", type="primary"):
        st.session_state["_per_cat_caps"] = {
            cat["name"]: st.session_state.get(f"cat_{i}", DEFAULT_CAP)
            for i, cat in enumerate(cats)
        }
        _save_form(exclude=st.session_state.get("s4_exclude",""))
        st.session_state.run_triggered = True
        st.session_state.step = 5
        st.rerun()

# ── Step 5 — Run & Results ────────────────────────────────────────────────────
elif step == 5:
    _f5    = st.session_state["_form"]
    client = _f5.get("client", "—")
    sector = _f5.get("sector", "")

    st.markdown('<div class="step-enter">', unsafe_allow_html=True)
    st.markdown(f'<div class="step-label">Step 5 of {N_STEPS}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="step-title"><em>{client}</em> · Mapping</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Layout: left panel | log ──────────────────────────────────────────────
    col_info, col_log = st.columns([2, 3], gap="large")

    with col_info:
        st.markdown(f'<div class="art-wrap">{SORBET_SVG}</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#fff;border:1px solid #EDD8E2;border-radius:16px;padding:18px 20px;margin-top:16px;">
          <div style="font-size:10px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:{color};margin-bottom:10px;">Mandate</div>
          <div style="font-size:14px;font-weight:600;color:#1C1412;margin-bottom:3px;">{client}</div>
          <div style="font-size:12px;color:#9B7080;">{sector} · {_f5.get('sub','')}</div>
          <div style="font-size:12px;color:#9B7080;margin-top:3px;">{_f5.get('geo','')} → {_f5.get('tgeo','Pan-India')}</div>
        </div>""", unsafe_allow_html=True)

        # Live stat tiles
        stat_area    = st.empty()
        cost_area    = st.empty()
        download_area = st.empty()

    with col_log:
        log_area   = st.empty()
        error_area = st.empty()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _render_log():
        lines = st.session_state.log_lines
        html  = "\n".join(_colorize(l) for l in lines)
        # auto-scroll: push content and use JS trick via a hidden anchor
        log_area.markdown(
            f'<div class="log-box" id="logbox">{html}'
            f'<div id="log-end"></div></div>'
            f'<script>var lb=document.getElementById("logbox");if(lb)lb.scrollTop=lb.scrollHeight;</script>',
            unsafe_allow_html=True,
        )

    def add_log(line: str):
        st.session_state.log_lines.append(line)
        _render_log()

    def _render_stats(done: int, total: int, usd: float):
        pct = int(done / total * 100) if total else 0
        stat_area.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px;">
          <div class="stat-tile"><div class="stat-val">{done}</div><div class="stat-label">Companies done</div></div>
          <div class="stat-tile"><div class="stat-val">{total}</div><div class="stat-label">Total found</div></div>
        </div>
        <div class="prog-strip" style="margin-top:12px;"><div class="prog-fill" style="width:{pct}%"></div></div>
        <div style="text-align:right;font-size:10px;color:#9B7080;margin-top:2px;">{pct}%</div>
        """, unsafe_allow_html=True)
        cost_area.markdown(
            f'<div class="stat-tile" style="margin-top:8px;">'
            f'<div class="stat-val">${usd:.3f}</div>'
            f'<div class="stat-label">API cost this run</div></div>',
            unsafe_allow_html=True,
        )

    # Restore log if already running (page rerender)
    if st.session_state.log_lines:
        _render_log()
    if st.session_state.get("_run_cost"):
        cs = st.session_state["_run_cost"]
        _render_stats(cs.get("done",0), cs.get("total",0), cs.get("usd",0))

    if st.session_state.excel_bytes:
        with col_info:
            download_area.download_button(
                "⬇ Download Excel",
                data=st.session_state.excel_bytes,
                file_name=st.session_state.excel_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    # ── Main run ──────────────────────────────────────────────────────────────
    if st.session_state.run_triggered:
        st.session_state.run_triggered = False
        st.session_state.log_lines     = []
        st.session_state.excel_bytes   = None
        st.session_state["_run_cost"]  = {}
        reset_cost()

        strategy = st.session_state.strategy
        cats     = strategy.get("categories", [])
        per_cat_caps = st.session_state.get("_per_cat_caps") or {
            cat["name"]: DEFAULT_CAP for cat in cats
        }

        inp      = _build_inp()
        date_tag = datetime.today().strftime("%d%b%y")
        filename = f"Accomplir - {inp['client']} - Mapping - {date_tag}.xlsx"

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as _tmp:
            tmp_path = _tmp.name
        _last_save = [0.0]
        _done_count = [0]
        _total_count = [0]

        class _Q(io.StringIO):
            def write(self, s): return super().write(s)

        def _save_partial(partial: dict):
            now = _time.monotonic()
            if now - _last_save[0] < 3.0: return
            _last_save[0] = now
            try:
                with contextlib.redirect_stdout(_Q()):
                    generate_excel(strategy, partial, inp, tmp_path)
                with open(tmp_path, "rb") as f:
                    data = f.read()
                n = sum(len(v) for v in partial.values())
                st.session_state.excel_bytes    = data
                st.session_state.excel_filename = filename
                usd = get_cost_summary()["usd"]
                _render_stats(n, _total_count[0], usd)
                with col_info:
                    download_area.download_button(
                        f"⬇ Download Excel  ({n} so far)",
                        data=data, file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="dl_partial",
                    )
            except Exception:
                pass

        try:
            add_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            add_log(f"  {'Sell-side' if inp['is_sellside'] else 'Buy-side'}  ·  {inp['client']}")
            add_log(f"  {inp['sector']}  ·  {inp['sub_sector']}  ·  {inp['geography']}")
            add_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            add_log("\n[1/4] Strategy ready  ✓")
            for c in cats:
                add_log(f"     • {c['name']}  ({per_cat_caps.get(c['name'], DEFAULT_CAP)} co.)")

            add_log("\n[2/4] Building universe…")
            discovered = discover_companies(
                cats, inp, on_progress=add_log, per_cat_caps=per_cat_caps)
            total_disc = sum(len(v) for v in discovered.values())
            _total_count[0] = total_disc
            add_log(f"\n  ✓ {total_disc} companies across {len(discovered)} categories")
            _render_stats(0, total_disc, get_cost_summary()["usd"])

            add_log(f"\n[3/4] Enriching {total_disc} companies…")

            # Wrap on_company_done to update progress tiles
            def _on_done(partial: dict):
                _done_count[0] = sum(len(v) for v in partial.values())
                _render_stats(_done_count[0], _total_count[0], get_cost_summary()["usd"])
                _save_partial(partial)

            enriched = enrich_all(
                discovered, inp, on_progress=add_log, on_company_done=_on_done)
            total_enr = sum(len(v) for v in enriched.values())
            add_log(f"\n  ✓ Done  —  {total_enr} companies enriched")

            add_log("\n[4/4] Writing Excel…")
            with contextlib.redirect_stdout(_Q()):
                generate_excel(strategy, enriched, inp, tmp_path)
            with open(tmp_path, "rb") as f:
                excel_bytes = f.read()
            os.unlink(tmp_path)

            st.session_state.excel_bytes    = excel_bytes
            st.session_state.excel_filename = filename

            cs  = get_cost_summary()
            usd = cs["usd"]
            st.session_state["_run_cost"] = {"done": total_enr, "total": total_enr, "usd": usd}
            _render_stats(total_enr, total_enr, usd)

            add_log(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            add_log(f"  DONE  ·  {total_enr} companies  ·  ${usd:.3f} API cost")
            add_log(f"  {cs['claude_calls']} Claude calls · {cs['serp_calls']} searches · {cs['apollo_calls']} Apollo")
            add_log(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            with col_info:
                download_area.download_button(
                    "⬇ Download Excel",
                    data=excel_bytes, file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_final",
                )

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            add_log(f"\n[ERROR] {type(e).__name__}: {e}")
            add_log(f"\n{tb}")
            error_area.markdown(
                f'<div class="err-banner">⚠ <strong>{type(e).__name__}</strong>: {e}<br>'
                f'<small style="opacity:.7">Check the log above for the full trace.</small></div>',
                unsafe_allow_html=True,
            )

    # Start over
    st.markdown("<br>", unsafe_allow_html=True)
    _, _, reset_col = st.columns([1, 3, 1])
    if reset_col.button("← Start Over", key="reset", type="secondary"):
        for k in ["step","strategy","log_lines","excel_bytes","excel_filename",
                  "run_triggered","_run_cost","_form","_per_cat_caps"]:
            st.session_state.pop(k, None)
        st.rerun()
