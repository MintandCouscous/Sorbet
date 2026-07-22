"""Automap — Streamlit UI for Accomplir Advisors M&A Mapping Tool"""

import contextlib
import io
import os
import tempfile
import time as _time
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

from automap import (
    MOTIVATIONS, COMPANY_TYPES, COUNT_OPTIONS,
    generate_strategy, discover_companies, enrich_all, generate_excel,
)

st.set_page_config(page_title="Sorbet · Accomplir", page_icon="🍧", layout="wide")

# ── Sorbet illustration ───────────────────────────────────────────────────────
SORBET_SVG = """
<svg viewBox="0 0 300 460" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="shine" cx="28%" cy="22%" r="55%">
      <stop offset="0%" stop-color="#fff" stop-opacity="0.72"/>
      <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="g-str" cx="35%" cy="28%" r="65%">
      <stop offset="0%" stop-color="#FFB3CB"/><stop offset="45%" stop-color="#FF4D7D"/>
      <stop offset="100%" stop-color="#B80044"/>
    </radialGradient>
    <radialGradient id="g-lem" cx="35%" cy="28%" r="65%">
      <stop offset="0%" stop-color="#FFFAAA"/><stop offset="45%" stop-color="#FFE234"/>
      <stop offset="100%" stop-color="#BF9800"/>
    </radialGradient>
    <radialGradient id="g-mnt" cx="35%" cy="28%" r="65%">
      <stop offset="0%" stop-color="#B8F4E8"/><stop offset="45%" stop-color="#3DD9B5"/>
      <stop offset="100%" stop-color="#0A9E80"/>
    </radialGradient>
    <linearGradient id="cone-g" x1="20%" y1="0%" x2="80%" y2="100%">
      <stop offset="0%" stop-color="#E8B030"/><stop offset="100%" stop-color="#8B5000"/>
    </linearGradient>
    <clipPath id="cone-clip"><polygon points="62,262 238,262 150,445"/></clipPath>
  </defs>
  <ellipse cx="150" cy="453" rx="72" ry="8" fill="#CCA878" opacity="0.4"/>
  <polygon points="62,262 238,262 150,445" fill="url(#cone-g)"/>
  <g clip-path="url(#cone-clip)" stroke="#6B3800" stroke-width="1.2" opacity="0.35">
    <line x1="48"  y1="248" x2="178" y2="455"/><line x1="84"  y1="248" x2="210" y2="448"/>
    <line x1="120" y1="248" x2="238" y2="440"/><line x1="156" y1="248" x2="258" y2="420"/>
    <line x1="192" y1="248" x2="272" y2="396"/>
    <line x1="252" y1="248" x2="124" y2="456"/><line x1="224" y1="248" x2="98"  y2="452"/>
    <line x1="196" y1="248" x2="74"  y2="446"/><line x1="168" y1="248" x2="54"  y2="434"/>
    <line x1="62"  y1="262" x2="238" y2="262"/>
    <line x1="82"  y1="300" x2="220" y2="300"/><line x1="100" y1="338" x2="202" y2="338"/>
    <line x1="118" y1="374" x2="184" y2="374"/><line x1="134" y1="408" x2="168" y2="408"/>
  </g>
  <ellipse cx="150" cy="262" rx="88" ry="12" fill="url(#cone-g)"/>
  <ellipse cx="150" cy="262" rx="88" ry="12" fill="#fff" opacity="0.2"/>
  <circle cx="150" cy="226" r="86" fill="url(#g-str)"/>
  <circle cx="150" cy="226" r="86" fill="url(#shine)"/>
  <path d="M118,306 Q112,326 110,340 Q108,350 114,351 Q120,352 122,342 Q124,330 124,310" fill="#FF4D7D" opacity="0.85"/>
  <path d="M182,304 Q188,322 186,334 Q184,344 179,343 Q174,342 176,332 Q178,320 180,306" fill="#B80044" opacity="0.75"/>
  <circle cx="143" cy="144" r="76" fill="url(#g-lem)"/>
  <circle cx="143" cy="144" r="76" fill="url(#shine)"/>
  <path d="M112,216 Q106,232 104,244 Q102,254 108,255 Q114,256 116,245 Q118,233 116,218" fill="#FFE234" opacity="0.85"/>
  <circle cx="156" cy="72" r="66" fill="url(#g-mnt)"/>
  <circle cx="156" cy="72" r="66" fill="url(#shine)"/>
  <g transform="translate(214,16) rotate(18)">
    <path d="M0,-13 Q9,-7 11,2 Q7,15 0,21 Q-7,15 -11,2 Q-9,-7 0,-13Z" fill="#E01848"/>
    <path d="M-2,-15 Q0,-9 2,-15" stroke="#5A9E20" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <ellipse cx="-1" cy="2"  rx="1.4" ry="2" fill="#FFB3C0" transform="rotate(-10 -1 2)"/>
    <ellipse cx="4"  cy="-3" rx="1.4" ry="2" fill="#FFB3C0" transform="rotate(15 4 -3)"/>
    <ellipse cx="3"  cy="9"  rx="1.4" ry="2" fill="#FFB3C0" transform="rotate(-5 3 9)"/>
  </g>
  <g transform="translate(96,22) rotate(-38)">
    <path d="M0,0 Q9,-17 0,-30 Q-9,-17 0,0Z" fill="#2DC8A0"/>
    <line x1="0" y1="0" x2="0" y2="-30" stroke="#1A9070" stroke-width="1.2" opacity="0.6"/>
  </g>
  <g transform="translate(84,12) rotate(-58)">
    <path d="M0,0 Q6,-12 0,-22 Q-6,-12 0,0Z" fill="#3DD9B5" opacity="0.85"/>
  </g>
  <g transform="translate(40,114)">
    <circle r="17" fill="#FFE234" stroke="#BF9800" stroke-width="1.5"/>
    <circle r="8.5" fill="#FFFAAA"/>
    <line x1="-17" y1="0"   x2="17" y2="0"   stroke="#BF9800" stroke-width="0.8" opacity="0.5"/>
    <line x1="0"   y1="-17" x2="0"  y2="17"  stroke="#BF9800" stroke-width="0.8" opacity="0.5"/>
    <line x1="-12" y1="-12" x2="12" y2="12"  stroke="#BF9800" stroke-width="0.8" opacity="0.5"/>
    <line x1="12"  y1="-12" x2="-12" y2="12" stroke="#BF9800" stroke-width="0.8" opacity="0.5"/>
  </g>
  <text x="264" y="68"  font-size="15" fill="#FF4D7D" class="sp1">&#x2726;</text>
  <text x="22"  y="172" font-size="11" fill="#FFE234" class="sp2">&#x2726;</text>
  <text x="272" y="188" font-size="9"  fill="#3DD9B5" class="sp3">&#x2726;</text>
  <text x="34"  y="84"  font-size="13" fill="#FF4D7D" class="sp2">&#x2726;</text>
  <text x="270" y="118" font-size="8"  fill="#FFE234" class="sp1">&#x2726;</text>
  <text x="50"  y="214" font-size="9"  fill="#3DD9B5" class="sp3">&#x2726;</text>
</svg>
"""

# ── Log colorizer ─────────────────────────────────────────────────────────────
def _colorize(line: str) -> str:
    s = line.rstrip()
    if not s.strip():
        return "<br>"
    esc = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if "━" in s:
        return f'<span style="color:#FF4D7D;opacity:0.45;">{esc}</span>'
    if s.lstrip().startswith("[") and "/4]" in s:
        return f'<span style="color:#FFB3CB;font-weight:700;">{esc}</span>'
    if "[ERROR]" in s:
        return f'<span style="color:#FF6B8A;text-decoration:underline;">{esc}</span>'
    if "✓" in s or "DONE" in s:
        return f'<span style="color:#fff;">{esc}</span>'
    if "↳" in s:
        return f'<span style="color:#9B7A8E;">{esc}</span>'
    return f'<span style="color:#C49AAE;">{esc}</span>'

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@1,9..144,300..700&family=Playfair+Display:ital,wght@0,600;1,500&family=Inter:wght@300;400;500;600;700&display=swap');

*, html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.stApp {
    background: #FFF5F8 !important;
    background-image:
        radial-gradient(circle at 15% 15%, rgba(255,77,125,0.07) 0%, transparent 45%),
        radial-gradient(circle at 85% 85%, rgba(61,217,181,0.06) 0%, transparent 45%),
        radial-gradient(circle at 70% 8%,  rgba(255,226,52,0.05) 0%, transparent 35%) !important;
}
.block-container { padding: 0 2.5rem 3rem !important; max-width: 100% !important; }

/* ── Hero banner ── */
.hero-banner {
    display: flex; align-items: center; gap: 0;
    background: linear-gradient(135deg,#fff8f5 0%,#fff0f6 60%,#f4fff8 100%);
    border-radius: 24px; border: 1px solid #FFE4EC;
    padding: 28px 36px 28px 44px;
    margin: 1.5rem 0 1.8rem;
    box-shadow: 0 4px 32px rgba(200,80,120,0.09);
    overflow: hidden; position: relative;
}
.hero-banner::before {
    content: ''; position: absolute; top:-60px; right:-40px;
    width:280px; height:280px; border-radius:50%;
    background: radial-gradient(circle,rgba(255,77,125,0.07) 0%,transparent 70%);
}
.hero-text { flex:1; z-index:1; }
.hero-title {
    font-family:'Fraunces',serif !important; font-style:italic !important;
    font-size: clamp(60px, 7.5vw, 100px);
    font-weight: 500; line-height: 0.87; letter-spacing: -0.02em;
    color: #8B1A42; display: block; margin: 0 0 14px;
}
.hero-tagline {
    font-family:'Playfair Display',serif; font-style:italic;
    font-size:15px; color:#B85880; line-height:1.58; max-width:380px;
}
.hero-pills { display:flex; gap:8px; margin-top:14px; flex-wrap:wrap; }
.fpill {
    font-size:10px; font-weight:700; letter-spacing:0.09em; text-transform:uppercase;
    padding:5px 13px; border-radius:20px;
    background:rgba(255,255,255,0.85); border:1.5px solid;
}
.fp-str { color:#CC1A50; border-color:#FFB3CB; }
.fp-lem { color:#9B7800; border-color:#FFE234; }
.fp-mnt { color:#0A9E80; border-color:#A8F0E0; }
.hero-by {
    font-size:10px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase;
    color:#CC7099; margin-top:16px; display:flex; align-items:center; gap:10px;
}
.hero-by::before { content:''; width:28px; height:1px; background:#CC7099; opacity:.5; display:inline-block; }
.hero-art {
    flex:0 0 auto; width:clamp(150px,17vw,230px);
    animation:float 5s ease-in-out infinite;
    filter:drop-shadow(0 18px 32px rgba(180,40,80,0.2)); z-index:1;
}
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-14px)} }
.sp1 { animation:sparkle 3.2s ease-in-out infinite; display:inline-block; }
.sp2 { animation:sparkle 3.2s ease-in-out 1.1s infinite; display:inline-block; }
.sp3 { animation:sparkle 3.2s ease-in-out 2.2s infinite; display:inline-block; }
@keyframes sparkle {
    0%,100%{opacity:.15;transform:scale(.6) rotate(0deg)}
    50%{opacity:1;transform:scale(1.3) rotate(20deg)}
}

/* ── Tile headers ── */
.tile-hdr {
    font-size:10.5px; font-weight:700; letter-spacing:0.13em; text-transform:uppercase;
    padding-bottom:10px; margin-bottom:2px; border-bottom:2px solid;
}
.th-deal  { color:#CC1A50; border-color:#FFB3CB; }
.th-mkt   { color:#9B7800; border-color:#FFE234; }
.th-motiv { color:#0A9E80; border-color:#3DD9B5; }
.th-filt  { color:#6B3AAA; border-color:#D4AAFF; }
.th-vol   { color:#C85000; border-color:#FFB380; }

/* ── Inputs ── */
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background:#FFFAFC !important; border:1.5px solid #F0D0DC !important;
    border-radius:10px !important; color:#1C1412 !important;
    font-size:13px !important; padding:9px 13px !important;
    transition:border-color .18s, box-shadow .18s !important;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
    border-color:#FF4D7D !important; box-shadow:0 0 0 3px rgba(255,77,125,.11) !important; outline:none !important;
}
.stTextInput>div>div>input::placeholder, .stTextArea>div>div>textarea::placeholder { color:#CCA8B8 !important; }
.stTextInput label, .stTextArea label {
    color:#8B5060 !important; font-size:11px !important; font-weight:600 !important; letter-spacing:.04em !important;
}
.stSelectbox div[data-baseweb="select"]>div {
    background:#FFFAFC !important; border-color:#F0D0DC !important;
    border-radius:10px !important; color:#1C1412 !important;
}
.stSelectbox label { color:#8B5060 !important; font-size:11px !important; font-weight:600 !important; }
div[data-testid="stRadioGroup"] label span { color:#1C1412 !important; font-size:12.5px !important; }
div[data-testid="stRadioGroup"]>label { color:#8B5060 !important; font-size:11px !important; font-weight:600 !important; }
.stCheckbox label p, .stCheckbox label span { color:#1C1412 !important; font-size:12px !important; }

/* ── Run button ── */
div[data-testid="stButton"]>button {
    background:linear-gradient(135deg,#FF4D7D 0%,#CC1A50 100%) !important;
    color:#fff !important; border:none !important; border-radius:14px !important;
    font-family:'Fraunces',serif !important; font-style:italic !important;
    font-size:20px !important; font-weight:500 !important;
    padding:18px 32px !important; width:100% !important; margin-top:14px !important;
    box-shadow:0 8px 28px rgba(200,26,80,.30) !important;
    transition:opacity .18s, transform .1s, box-shadow .18s !important;
}
div[data-testid="stButton"]>button:hover {
    opacity:.91 !important; transform:translateY(-2px) !important;
    box-shadow:0 12px 36px rgba(200,26,80,.36) !important;
}
div[data-testid="stButton"]>button:active { transform:translateY(0) !important; }

/* ── Download button ── */
div[data-testid="stDownloadButton"]>button {
    background:#fff !important; color:#CC1A50 !important;
    border:2px solid #FF4D7D !important; border-radius:12px !important;
    font-family:'Fraunces',serif !important; font-style:italic !important;
    font-size:16px !important; font-weight:500 !important;
    padding:13px 24px !important; width:100% !important; margin-top:8px !important;
    box-shadow:0 2px 14px rgba(255,77,125,.14) !important;
}
div[data-testid="stDownloadButton"]>button:hover { background:#FFF5F8 !important; }

/* ── Log ── */
.log-box {
    background:#1C0814; border:1px solid rgba(255,77,125,.2); border-radius:16px;
    padding:20px 22px; font-family:monospace; font-size:11.5px; line-height:1.9;
    max-height:440px; overflow-y:auto; white-space:pre-wrap; word-break:break-all; margin-top:16px;
}
.log-box::-webkit-scrollbar { width:4px; }
.log-box::-webkit-scrollbar-thumb { background:#FF4D7D; border-radius:2px; }

/* ── Container borders ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-color:#FFE4EC !important; border-radius:16px !important;
    background:rgba(255,255,255,.88) !important; padding:16px 18px 18px !important;
    box-shadow:0 2px 14px rgba(200,80,120,.07) !important;
}

#MainMenu, footer, header { visibility:hidden; }
hr { border-color:#FFD0E0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero banner (full-width HTML, no Streamlit columns) ───────────────────────
st.markdown(f"""
<div class="hero-banner">
  <div class="hero-text">
    <span class="hero-title">Sorbet</span>
    <div class="hero-tagline">
      Like sorbet between courses —<br>
      a fresh, clear view of the market before the deal.
    </div>
    <div class="hero-pills">
      <span class="fpill fp-str">🍓 Discover</span>
      <span class="fpill fp-lem">🍋 Enrich</span>
      <span class="fpill fp-mnt">🌿 Export</span>
    </div>
    <div class="hero-by">Accomplir Advisors</div>
  </div>
  <div class="hero-art">{SORBET_SVG}</div>
</div>
""", unsafe_allow_html=True)

# ── Form tiles (level-0 columns → checkboxes inside use level-1 OK) ──────────
row1_a, row1_b = st.columns(2, gap="medium")

with row1_a:
    with st.container(border=True):
        st.markdown('<div class="tile-hdr th-deal">🍓 The Deal</div>', unsafe_allow_html=True)
        mandate_type = st.radio("Mandate type", ["Sell-side", "Buy-side"], horizontal=True)
        is_sellside  = mandate_type == "Sell-side"
        client       = st.text_input("Client company", placeholder="e.g. Cessna Lifeline")
        role         = "company being sold" if is_sellside else "acquirer"
        company_desc = st.text_area(f"Describe the {role}",
            placeholder="Products, size, geography, deal context — paste freely", height=90)

with row1_b:
    with st.container(border=True):
        st.markdown('<div class="tile-hdr th-mkt">🍋 The Market</div>', unsafe_allow_html=True)
        f1, f2 = st.columns(2)
        sector     = f1.text_input("Sector",     placeholder="Healthcare")
        sub_sector = f2.text_input("Sub-sector", placeholder="Veterinary Care")
        f3, f4 = st.columns(2)
        geography        = f3.text_input("Client HQ",         placeholder="Bengaluru")
        target_geography = f4.text_input("Target geography",  placeholder="Pan-India")

row2_a, row2_b = st.columns(2, gap="medium")

with row2_a:
    with st.container(border=True):
        st.markdown('<div class="tile-hdr th-motiv">🌿 M&A Motivations</div>', unsafe_allow_html=True)
        motivations = []
        mc1, mc2 = st.columns(2)
        for i, m in enumerate(MOTIVATIONS):
            col = mc1 if i % 2 == 0 else mc2
            if col.checkbox(m, key=f"mot_{i}"):
                motivations.append(m)

with row2_b:
    with st.container(border=True):
        st.markdown('<div class="tile-hdr th-filt">🍇 Target Filters</div>', unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        revenue_range    = g1.text_input("Revenue range",   placeholder=">100 Cr")
        specific_attrs   = g2.text_input("Must-have attrs", placeholder="PLI / CRISIL")
        what_looking_for = st.text_input("What are you seeking?",
            placeholder="East India expansion / R&D capabilities")
        st.markdown('<div style="font-size:11px;font-weight:600;color:#8B5060;letter-spacing:.04em;margin:10px 0 4px;">COMPANY TYPES</div>', unsafe_allow_html=True)
        tc1, tc2 = st.columns(2)
        company_types = []
        for i, ct in enumerate(COMPANY_TYPES):
            col = tc1 if i % 2 == 0 else tc2
            if col.checkbox(ct, value=True, key=f"ct_{i}"):
                company_types.append(ct)

# ── Volume tile (full-width) ──────────────────────────────────────────────────
with st.container(border=True):
    st.markdown('<div class="tile-hdr th-vol">🍊 Volume & Exclusions</div>', unsafe_allow_html=True)
    vl, vr = st.columns([3, 2], gap="large")
    with vl:
        count_labels = [v[0] for v in COUNT_OPTIONS.values()]
        count_choice = st.radio("Companies to map", count_labels, index=3, horizontal=True)
        per_cat_cap  = next(cap for lbl, cap in COUNT_OPTIONS.values() if lbl == count_choice)
    with vr:
        exclude_companies = st.text_area("Already mapped — skip these",
            placeholder="One per line or comma-separated", height=72)

inp = {
    "is_sellside":       is_sellside,
    "client":            client.strip(),
    "company_desc":      company_desc.strip(),
    "sector":            sector.strip(),
    "sub_sector":        sub_sector.strip(),
    "geography":         geography.strip(),
    "motivations":       motivations,
    "target_geography":  target_geography.strip() or "Pan-India",
    "revenue_range":     revenue_range.strip()    or "No filter",
    "specific_attrs":    specific_attrs.strip()   or "None",
    "what_looking_for":  what_looking_for.strip() or "None",
    "company_types":     company_types,
    "exclude_companies": exclude_companies.strip(),
    "per_cat_cap":       per_cat_cap,
    "count_label":       count_choice,
    "date":              datetime.today().strftime("%d-%b-%y"),
}

# ── Run button ────────────────────────────────────────────────────────────────
run_btn = st.button("Run Mapping →")

log_area      = st.empty()
download_area = st.empty()

for k in ("log_lines", "excel_bytes", "excel_filename"):
    if k not in st.session_state:
        st.session_state[k] = [] if k == "log_lines" else (None if k == "excel_bytes" else "")

def _render_log():
    html = "\n".join(_colorize(l) for l in st.session_state.log_lines)
    log_area.markdown(f'<div class="log-box">{html}</div>', unsafe_allow_html=True)

def add_log(line: str):
    st.session_state.log_lines.append(line)
    _render_log()

if st.session_state.log_lines:
    _render_log()

if st.session_state.excel_bytes:
    download_area.download_button(
        label="Download Excel",
        data=st.session_state.excel_bytes,
        file_name=st.session_state.excel_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

if "discovered_checkpoint" in st.session_state and not st.session_state.excel_bytes:
    disc = st.session_state.discovered_checkpoint
    st.info(f"Discovery done: {sum(len(v) for v in disc.values())} companies found. "
            "Enrichment may have been interrupted — re-run to continue.")

if run_btn:
    errs = []
    if not client.strip():       errs.append("Client name is required.")
    if not company_desc.strip(): errs.append("Company description is required.")
    if not sector.strip():       errs.append("Sector is required.")
    if not sub_sector.strip():   errs.append("Sub-sector is required.")
    if not geography.strip():    errs.append("Client geography is required.")
    if not motivations:          errs.append("Select at least one M&A motivation.")
    if not company_types:        errs.append("Select at least one company type.")
    if errs:
        for e in errs: st.error(e)
        st.stop()

    st.session_state.log_lines   = []
    st.session_state.excel_bytes = None
    download_area.empty()

    date_tag = datetime.today().strftime("%d%b%y")
    filename = f"Accomplir - {client} - Mapping - {date_tag}.xlsx"

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as _tmp:
        tmp_path = _tmp.name

    _last_save = [0.0]

    class _Q(io.StringIO):
        def write(self, s): return super().write(s)

    def _save_partial(partial_enriched: dict):
        now = _time.monotonic()
        if now - _last_save[0] < 3.0:
            return
        _last_save[0] = now
        try:
            with contextlib.redirect_stdout(_Q()):
                generate_excel(strategy, partial_enriched, inp, tmp_path)
            with open(tmp_path, "rb") as f:
                data = f.read()
            n = sum(len(v) for v in partial_enriched.values())
            st.session_state.excel_bytes    = data
            st.session_state.excel_filename = filename
            download_area.download_button(
                label=f"Download Excel  ({n} companies so far)",
                data=data, file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_partial",
            )
        except Exception:
            pass

    try:
        add_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        add_log(f"  {'Sell-side' if is_sellside else 'Buy-side'}  ·  {client}")
        add_log(f"  {sector}  ·  {sub_sector}  ·  {geography}")
        add_log(f"  Volume: {count_choice}")
        add_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        add_log("\n[1/4] Generating mapping strategy…")
        with contextlib.redirect_stdout(_Q()):
            strategy = generate_strategy(inp)
        add_log(f"  ✓ {len(strategy['categories'])} categories identified")
        for c in strategy["categories"]:
            add_log(f"     • {c['name']}")

        add_log(f"\n[2/4] Building universe…")
        discovered = discover_companies(
            strategy["categories"], inp, on_progress=add_log)
        total_disc = sum(len(v) for v in discovered.values())
        st.session_state.discovered_checkpoint = discovered
        add_log(f"\n  ✓ {total_disc} companies across {len(discovered)} categories")

        add_log(f"\n[3/4] Enriching {total_disc} companies…")
        enriched = enrich_all(
            discovered, inp, on_progress=add_log, on_company_done=_save_partial)
        add_log(f"\n  ✓ Enrichment complete  —  {sum(len(v) for v in enriched.values())} companies")

        add_log("\n[4/4] Writing Excel…")
        with contextlib.redirect_stdout(_Q()):
            generate_excel(strategy, enriched, inp, tmp_path)
        add_log("     ↳ Snapshot  ✓")
        add_log(f"     ↳ {len(enriched)} mapping sheets  ✓")
        add_log("     ↳ Decision makers  ✓")

        with open(tmp_path, "rb") as f:
            excel_bytes = f.read()
        os.unlink(tmp_path)

        st.session_state.excel_bytes    = excel_bytes
        st.session_state.excel_filename = filename

        total = sum(len(v) for v in enriched.values())
        add_log(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        add_log(f"  DONE  ·  {total} companies  ·  {len(enriched)} categories")
        add_log(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        download_area.download_button(
            label="Download Excel",
            data=excel_bytes, file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_final",
        )

    except Exception as e:
        add_log(f"\n[ERROR] {e}")
        st.error(f"Something went wrong: {e}")
