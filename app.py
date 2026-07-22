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

st.set_page_config(
    page_title="Sorbet · Accomplir",
    page_icon="🍧",
    layout="wide",
)

# ── French ice cream cart SVG ─────────────────────────────────────────────────
CART_SVG = """
<svg viewBox="0 0 400 290" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="sg" cx="35%" cy="30%" r="60%">
      <stop offset="0%" stop-color="#fff" stop-opacity="0.65"/>
      <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="sg2" cx="35%" cy="30%" r="60%">
      <stop offset="0%" stop-color="#fff" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- Shadow -->
  <ellipse cx="200" cy="284" rx="148" ry="8" fill="#C9B48A" opacity="0.35"/>

  <!-- ── Wheels ── -->
  <!-- Left wheel outer ring -->
  <circle cx="82" cy="238" r="44" fill="#5C3A18" stroke="#C49A35" stroke-width="3"/>
  <circle cx="82" cy="238" r="30" fill="#7A5220" stroke="#C49A35" stroke-width="1.5"/>
  <!-- Left spokes -->
  <g stroke="#C49A35" stroke-width="1.8" opacity="0.9">
    <line x1="82" y1="194" x2="82" y2="282"/>
    <line x1="38" y1="238" x2="126" y2="238"/>
    <line x1="51" y1="207" x2="113" y2="269"/>
    <line x1="51" y1="269" x2="113" y2="207"/>
  </g>
  <circle cx="82" cy="238" r="7" fill="#C49A35"/>

  <!-- Right wheel outer ring -->
  <circle cx="318" cy="238" r="44" fill="#5C3A18" stroke="#C49A35" stroke-width="3"/>
  <circle cx="318" cy="238" r="30" fill="#7A5220" stroke="#C49A35" stroke-width="1.5"/>
  <!-- Right spokes -->
  <g stroke="#C49A35" stroke-width="1.8" opacity="0.9">
    <line x1="318" y1="194" x2="318" y2="282"/>
    <line x1="274" y1="238" x2="362" y2="238"/>
    <line x1="287" y1="207" x2="349" y2="269"/>
    <line x1="287" y1="269" x2="349" y2="207"/>
  </g>
  <circle cx="318" cy="238" r="7" fill="#C49A35"/>

  <!-- Axle -->
  <line x1="82" y1="238" x2="318" y2="238" stroke="#C49A35" stroke-width="2.5" opacity="0.3"/>

  <!-- ── Cart body ── -->
  <rect x="52" y="155" width="280" height="78" rx="5" fill="#7A5220"/>
  <!-- Plank lines -->
  <line x1="52" y1="175" x2="332" y2="175" stroke="#5C3A18" stroke-width="1.2" opacity="0.45"/>
  <line x1="52" y1="195" x2="332" y2="195" stroke="#5C3A18" stroke-width="1.2" opacity="0.45"/>
  <line x1="52" y1="215" x2="332" y2="215" stroke="#5C3A18" stroke-width="1.2" opacity="0.45"/>
  <!-- Cart border -->
  <rect x="50" y="153" width="284" height="82" rx="6" fill="none" stroke="#C49A35" stroke-width="2.5"/>

  <!-- "Glaces" script on cart -->
  <text x="192" y="201" text-anchor="middle" font-family="Fraunces, Georgia, serif"
        font-size="19" font-style="italic" fill="#C49A35" opacity="0.88">Glaces</text>

  <!-- ── Counter surface ── -->
  <rect x="42" y="143" width="300" height="16" rx="3" fill="#C49A35"/>
  <rect x="42" y="143" width="300" height="6" rx="3" fill="#E8BF60" opacity="0.55"/>

  <!-- ── Ice cream tubs + scoops ── -->
  <!-- Strawberry -->
  <ellipse cx="102" cy="137" rx="22" ry="9" fill="#F2A8B0"/>
  <rect x="80" y="127" width="44" height="16" fill="#F2A8B0"/>
  <ellipse cx="102" cy="127" rx="22" ry="9" fill="#FFD0D8"/>
  <circle cx="102" cy="115" r="17" fill="#FF8FAE"/>
  <circle cx="102" cy="115" r="17" fill="url(#sg)"/>

  <!-- Pistachio -->
  <ellipse cx="162" cy="137" rx="22" ry="9" fill="#7EC8A0"/>
  <rect x="140" y="127" width="44" height="16" fill="#7EC8A0"/>
  <ellipse cx="162" cy="127" rx="22" ry="9" fill="#AADCBC"/>
  <circle cx="162" cy="115" r="17" fill="#5BBB88"/>
  <circle cx="162" cy="115" r="17" fill="url(#sg)"/>

  <!-- Vanilla -->
  <ellipse cx="222" cy="137" rx="22" ry="9" fill="#E8C87A"/>
  <rect x="200" y="127" width="44" height="16" fill="#E8C87A"/>
  <ellipse cx="222" cy="127" rx="22" ry="9" fill="#F5DFA0"/>
  <circle cx="222" cy="115" r="17" fill="#F0CC58"/>
  <circle cx="222" cy="115" r="17" fill="url(#sg)"/>

  <!-- Chocolate -->
  <ellipse cx="282" cy="137" rx="22" ry="9" fill="#8B5E3C"/>
  <rect x="260" y="127" width="44" height="16" fill="#8B5E3C"/>
  <ellipse cx="282" cy="127" rx="22" ry="9" fill="#A87450"/>
  <circle cx="282" cy="115" r="17" fill="#6B4220"/>
  <circle cx="282" cy="115" r="17" fill="url(#sg2)"/>

  <!-- ── Awning poles ── -->
  <rect x="58" y="70" width="7" height="77" fill="#1A2B5E"/>
  <rect x="335" y="70" width="7" height="77" fill="#1A2B5E"/>

  <!-- ── Awning body — navy + cream stripes ── -->
  <rect x="22" y="22" width="356" height="52" fill="#1A2B5E"/>
  <!-- Cream stripes (every ~33px, 15px wide) -->
  <rect x="30"  y="22" width="15" height="52" fill="#F9F3E3" opacity="0.88"/>
  <rect x="63"  y="22" width="15" height="52" fill="#F9F3E3" opacity="0.88"/>
  <rect x="96"  y="22" width="15" height="52" fill="#F9F3E3" opacity="0.88"/>
  <rect x="129" y="22" width="15" height="52" fill="#F9F3E3" opacity="0.88"/>
  <rect x="162" y="22" width="15" height="52" fill="#F9F3E3" opacity="0.88"/>
  <rect x="195" y="22" width="15" height="52" fill="#F9F3E3" opacity="0.88"/>
  <rect x="228" y="22" width="15" height="52" fill="#F9F3E3" opacity="0.88"/>
  <rect x="261" y="22" width="15" height="52" fill="#F9F3E3" opacity="0.88"/>
  <rect x="294" y="22" width="15" height="52" fill="#F9F3E3" opacity="0.88"/>
  <rect x="327" y="22" width="15" height="52" fill="#F9F3E3" opacity="0.88"/>
  <rect x="360" y="22" width="18" height="52" fill="#F9F3E3" opacity="0.88"/>
  <!-- Top gold trim -->
  <rect x="22" y="20" width="356" height="4" fill="#C49A35"/>

  <!-- ── Scalloped fringe ── -->
  <path d="M22,74 Q28,88 34,74 Q40,88 46,74 Q52,88 58,74 Q64,88 70,74 Q76,88 82,74 Q88,88 94,74 Q100,88 106,74 Q112,88 118,74 Q124,88 130,74 Q136,88 142,74 Q148,88 154,74 Q160,88 166,74 Q172,88 178,74 Q184,88 190,74 Q196,88 202,74 Q208,88 214,74 Q220,88 226,74 Q232,88 238,74 Q244,88 250,74 Q256,88 262,74 Q268,88 274,74 Q280,88 286,74 Q292,88 298,74 Q304,88 310,74 Q316,88 322,74 Q328,88 334,74 Q340,88 346,74 Q352,88 358,74 Q364,88 370,74 Q376,88 378,74" fill="none" stroke="#C49A35" stroke-width="1.5"/>
  <path d="M22,74 Q28,88 34,74 Q40,88 46,74 Q52,88 58,74 Q64,88 70,74 Q76,88 82,74 Q88,88 94,74 Q100,88 106,74 Q112,88 118,74 Q124,88 130,74 Q136,88 142,74 Q148,88 154,74 Q160,88 166,74 Q172,88 178,74 Q184,88 190,74 Q196,88 202,74 Q208,88 214,74 Q220,88 226,74 Q232,88 238,74 Q244,88 250,74 Q256,88 262,74 Q268,88 274,74 Q280,88 286,74 Q292,88 298,74 Q304,88 310,74 Q316,88 322,74 Q328,88 334,74 Q340,88 346,74 Q352,88 358,74 Q364,88 370,74 Q376,88 378,74 L378,76 L22,76 Z" fill="#1A2B5E"/>

  <!-- ── Handle ── -->
  <path d="M338 155 Q368 155 372 138 Q376 120 360 116" stroke="#C49A35" stroke-width="4" fill="none" stroke-linecap="round"/>

  <!-- ── Sparkles ── -->
  <text x="346" y="106" font-size="10" fill="#C49A35" class="sp1">✦</text>
  <text x="60"  y="108" font-size="8"  fill="#FF8FAE" class="sp2">✦</text>
  <text x="195" y="100" font-size="7"  fill="#E8BF60" class="sp3">✦</text>
</svg>
"""

# ── Log colorizer ─────────────────────────────────────────────────────────────
def _colorize(line: str) -> str:
    s = line.rstrip()
    if not s.strip():
        return "<br>"
    esc = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if "━" in s or "═" in s:
        return f'<span style="color:#C49A35;opacity:0.7;">{esc}</span>'
    if s.lstrip().startswith("[") and "/4]" in s:
        return f'<span style="color:#E8BF60;font-weight:700;">{esc}</span>'
    if "[ERROR]" in s:
        return f'<span style="color:#E07B70;text-decoration:underline;">{esc}</span>'
    if "→" in s or "DONE" in s or "✓" in s:
        return f'<span style="color:#fff;">{esc}</span>'
    if s.startswith("     •"):
        return f'<span style="color:#8B9BB8;">{esc}</span>'
    return f'<span style="color:#A8B4CC;">{esc}</span>'

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@1,9..144,500..700&family=Playfair+Display:ital,wght@0,600;1,500&family=Inter:wght@300;400;500;600&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: #F9F3E3 !important;
    background-image: radial-gradient(circle, rgba(196,154,53,0.12) 1px, transparent 1px) !important;
    background-size: 26px 26px !important;
}

.block-container {
    padding: 0 2.5rem 2rem !important;
    max-width: 100% !important;
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 28px 0 4px;
}
.cart-wrap {
    display: inline-block;
    animation: float 5s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-11px); }
}
.sp1 { animation: sparkle 3s ease-in-out infinite; }
.sp2 { animation: sparkle 3s ease-in-out infinite 1s; }
.sp3 { animation: sparkle 3s ease-in-out infinite 2s; }
@keyframes sparkle {
    0%, 100% { opacity: 0.2; transform: scale(0.7); }
    50%       { opacity: 1;   transform: scale(1.2); }
}
.hero-illus {
    width: 200px;
    max-width: 55vw;
    margin: 0 auto;
    filter: drop-shadow(0 12px 20px rgba(92,58,24,0.18));
}
.hero-title {
    font-family: 'Fraunces', serif;
    font-optical-sizing: auto;
    font-variation-settings: "opsz" 144, "SOFT" 60, "WONK" 1;
    font-style: italic;
    font-size: 116px;
    font-weight: 600;
    letter-spacing: -0.01em;
    line-height: 0.95;
    color: #1A2B5E;
    margin-top: 6px;
    display: inline-block;
}
.hero-rule {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-top: 18px;
}
.hero-rule .ln {
    width: 56px;
    height: 1px;
    background: #C49A35;
}
.hero-rule .fleur {
    font-size: 13px;
    color: #C49A35;
    letter-spacing: 6px;
}
.hero-tag {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 14px;
    color: #6B5A3A;
    margin-top: 10px;
    letter-spacing: 0.01em;
}
.hero-why {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    color: #B8A888;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 10px;
}

/* ── Section labels ── */
.sec {
    font-family: 'Playfair Display', serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.06em;
    color: #1A2B5E;
    text-transform: uppercase;
    border-bottom: 1.5px solid #C49A35;
    padding-bottom: 7px;
    margin: 28px 0 14px;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #FFFDF7 !important;
    border: 1.5px solid #D8C8A8 !important;
    border-radius: 10px !important;
    color: #1C1412 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #C49A35 !important;
    box-shadow: 0 0 0 3px rgba(196,154,53,0.15) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #B8A888 !important;
}

/* ── Labels ── */
.stTextInput label, .stTextArea label {
    color: #6B5A3A !important;
    font-size: 11.5px !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
}

/* ── Radio / checkbox ── */
div[data-testid="stRadioGroup"] > div > label {
    color: #1C1412 !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
}
.stCheckbox label span {
    color: #1C1412 !important;
    font-size: 12.5px !important;
}
.stCheckbox > label {
    color: #6B5A3A !important;
    font-size: 11px !important;
}

/* ── Number input ── */
.stNumberInput input {
    background: #FFFDF7 !important;
    border: 1.5px solid #D8C8A8 !important;
    border-radius: 8px !important;
    color: #1C1412 !important;
    font-size: 13px !important;
}
.stNumberInput input:focus {
    border-color: #C49A35 !important;
    outline: none !important;
}
.stNumberInput label {
    color: #1A2B5E !important;
    font-size: 11.5px !important;
    font-weight: 600 !important;
}

/* ── Sub label ── */
.sub-lbl {
    font-size: 11.5px;
    font-weight: 600;
    letter-spacing: 0.04em;
    color: #6B5A3A;
    margin: 14px 0 8px;
}

/* ── Buttons ── */
div[data-testid="stButton"] > button {
    background: #1A2B5E !important;
    color: #F9F3E3 !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    padding: 13px 28px !important;
    width: 100% !important;
    margin-top: 10px !important;
    transition: background 0.18s, transform 0.1s !important;
}
div[data-testid="stButton"] > button:hover {
    background: #243F8A !important;
}

/* ── Secondary / reset button ── */
button[kind="secondary"],
div[data-testid="stButton"] > button.secondary {
    background: transparent !important;
    color: #1A2B5E !important;
    border: 1.5px solid #C49A35 !important;
}

/* ── Download button ── */
div[data-testid="stDownloadButton"] > button {
    background: #FFFDF7 !important;
    color: #1A2B5E !important;
    border: 1.5px solid #C49A35 !important;
    border-radius: 10px !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    width: 100% !important;
    margin-top: 6px !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: #F9F3E3 !important;
}

/* ── Log terminal ── */
.log-box {
    background: #0D1530;
    border: 1px solid #1A2B5E;
    border-radius: 14px;
    padding: 20px 22px;
    font-family: 'Inter', monospace;
    font-size: 12px;
    line-height: 1.9;
    max-height: 500px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
}
.log-box::-webkit-scrollbar { width: 4px; }
.log-box::-webkit-scrollbar-track { background: transparent; }
.log-box::-webkit-scrollbar-thumb { background: #C49A35; border-radius: 2px; }

/* ── Per-category box ── */
.cat-caps-box {
    background: #FFFDF7;
    border: 1px solid #D8C8A8;
    border-radius: 12px;
    padding: 16px 18px;
    margin: 8px 0 12px;
}
.cat-total {
    font-family: 'Playfair Display', serif;
    font-size: 12px;
    color: #1A2B5E;
    text-align: right;
    margin-top: 6px;
    letter-spacing: 0.03em;
}

/* ── Misc ── */
hr { border-color: #D8C8A8 !important; }
[data-testid="stHorizontalBlock"] { gap: 2.5rem; }
div[data-testid="stAlert"] { border-radius: 10px !important; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="cart-wrap">
    <div class="hero-illus">{CART_SVG}</div>
  </div>
  <div class="hero-title">Sorbet</div>
  <div class="hero-tag">Automated M&amp;A mapping, by Accomplir Advisors</div>
  <div class="hero-rule">
    <span class="ln"></span>
    <span class="fleur">✦ ✦ ✦</span>
    <span class="ln"></span>
  </div>
  <div class="hero-why">
    Like sorbet between courses — a clean, sharp view of the market before the deal.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
col_form, col_out = st.columns([10, 11], gap="large")

with col_form:

    st.markdown('<div class="sec">Mandate</div>', unsafe_allow_html=True)

    mandate_type = st.radio(
        "Type",
        ["Sell-side  (company looking to sell)", "Buy-side  (company looking to acquire)"],
        label_visibility="collapsed",
    )
    is_sellside = mandate_type.startswith("Sell")

    client       = st.text_input("Client / company name",        placeholder="e.g. Cessna Lifeline Veterinary Healthcare")
    role         = "company being sold" if is_sellside else "acquirer"
    company_desc = st.text_area(f"Describe the company ({role})",
                                placeholder="Products, scale, geography, any special context — paste freely",
                                height=100)

    c1, c2 = st.columns(2)
    with c1:
        sector     = st.text_input("Sector",     placeholder="Healthcare Services")
    with c2:
        sub_sector = st.text_input("Sub-sector", placeholder="Veterinary Care")

    geography = st.text_input("Client geography", placeholder="Bengaluru, Karnataka")

    st.markdown('<div class="sec">M&A Motivations</div>', unsafe_allow_html=True)
    motivation_cols = st.columns(2)
    motivations = []
    for i, m in enumerate(MOTIVATIONS):
        if motivation_cols[i % 2].checkbox(m, key=f"mot_{i}"):
            motivations.append(m)

    st.markdown(
        '<div class="sec">Target Filters '
        '<span style="font-weight:400;color:#B8A888;font-size:11px;text-transform:none;">— all optional</span></div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        target_geography = st.text_input("Target geography",    placeholder="Pan-India / South India")
        revenue_range    = st.text_input("Revenue range",        placeholder=">100 Cr  or  50–500 Cr")
    with c2:
        specific_attrs   = st.text_input("Must-have attributes", placeholder="manufacturing / CRISIL rated")
        what_looking_for = st.text_input("Specifically seeking", placeholder="Eastern India / R&D")

    st.markdown('<div class="sub-lbl">Company types to include</div>', unsafe_allow_html=True)
    type_cols = st.columns(2)
    company_types = []
    for i, ct in enumerate(COMPANY_TYPES):
        if type_cols[i % 2].checkbox(ct, value=True, key=f"ct_{i}"):
            company_types.append(ct)

    exclude_companies = st.text_area(
        "Already mapped — exclude these",
        placeholder="One company per line (or comma-separated). They'll be skipped entirely.",
        height=80,
    )

    st.markdown('<div class="sec">Volume</div>', unsafe_allow_html=True)
    count_labels = [v[0] for v in COUNT_OPTIONS.values()]
    count_choice = st.radio("Companies to map", count_labels, index=3, label_visibility="collapsed")
    default_cap  = next(cap for lbl, cap in COUNT_OPTIONS.values() if lbl == count_choice)

    # ── Build inp dict (used by both buttons) ─────────────────────────────────
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
        "per_cat_cap":       default_cap,
        "count_label":       count_choice,
        "date":              datetime.today().strftime("%d-%b-%y"),
    }

    def _validate():
        errs = []
        if not client.strip():       errs.append("Client name is required.")
        if not company_desc.strip(): errs.append("Company description is required.")
        if not sector.strip():       errs.append("Sector is required.")
        if not sub_sector.strip():   errs.append("Sub-sector is required.")
        if not geography.strip():    errs.append("Client geography is required.")
        if not motivations:          errs.append("Select at least one M&A motivation.")
        if not company_types:        errs.append("Select at least one company type.")
        return errs

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Phase 1: Generate Strategy button ─────────────────────────────────────
    gen_btn = st.button("Generate Strategy →", key="gen_btn")

    if gen_btn:
        errs = _validate()
        if errs:
            for e in errs:
                st.error(e)
        else:
            class _Q(io.StringIO):
                def write(self, s): return super().write(s)
            with st.spinner("Generating mapping strategy…"):
                with contextlib.redirect_stdout(_Q()):
                    strategy = generate_strategy(inp)
            st.session_state.strategy = strategy

    # ── Phase 2: Per-category count inputs + Run button ───────────────────────
    per_cat_caps = None
    run_btn      = False

    if "strategy" in st.session_state:
        strategy = st.session_state.strategy
        cats     = strategy.get("categories", [])

        st.markdown('<div class="sec">Companies per Category</div>', unsafe_allow_html=True)
        st.markdown('<div class="cat-caps-box">', unsafe_allow_html=True)

        per_cat_caps = {}
        for cat in cats:
            per_cat_caps[cat["name"]] = st.number_input(
                cat["name"],
                min_value=1,
                max_value=500,
                value=default_cap,
                step=5,
                key=f"pcc_{cat['name']}",
            )

        total_est = sum(per_cat_caps.values())
        st.markdown(f'<div class="cat-total">≈ {total_est} companies total</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns([3, 1])
        with c1:
            run_btn = st.button("Run Mapping", key="run_btn")
        with c2:
            if st.button("↺ Reset", key="reset_btn"):
                del st.session_state["strategy"]

# ── Output ────────────────────────────────────────────────────────────────────
with col_out:

    st.markdown('<div class="sec">The Scoop</div>', unsafe_allow_html=True)
    log_area      = st.empty()
    download_area = st.empty()

    if "log_lines" not in st.session_state:
        st.session_state.log_lines = []
    if "excel_bytes" not in st.session_state:
        st.session_state.excel_bytes = None
    if "excel_filename" not in st.session_state:
        st.session_state.excel_filename = ""

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

    # Show discovered companies count if enrichment was interrupted mid-run
    if "discovered_checkpoint" in st.session_state and not st.session_state.excel_bytes:
        disc = st.session_state.discovered_checkpoint
        total_disc = sum(len(v) for v in disc.values())
        st.info(f"Discovery completed: {total_disc} companies found. Enrichment may have been interrupted — re-run to continue.")

    if run_btn:
        errs = _validate()
        if errs:
            for e in errs:
                st.error(e)
            st.stop()

        st.session_state.log_lines   = []
        st.session_state.excel_bytes = None
        download_area.empty()

        date_tag = datetime.today().strftime("%d%b%y")
        filename = f"Accomplir - {client} - Mapping - {date_tag}.xlsx"

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as _tmp:
            tmp_path = _tmp.name

        _last_save = [0.0]

        strategy = st.session_state.strategy

        def _save_partial(partial_enriched: dict):
            now = _time.monotonic()
            if now - _last_save[0] < 3.0:
                return
            _last_save[0] = now
            try:
                class _Q(io.StringIO):
                    def write(self, s): return super().write(s)
                with contextlib.redirect_stdout(_Q()):
                    generate_excel(strategy, partial_enriched, inp, tmp_path)
                with open(tmp_path, "rb") as f:
                    data = f.read()
                n = sum(len(v) for v in partial_enriched.values())
                st.session_state.excel_bytes    = data
                st.session_state.excel_filename = filename
                download_area.download_button(
                    label=f"Download Excel  ({n} companies so far)",
                    data=data,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_partial",
                )
            except Exception:
                pass

        try:
            add_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            add_log(f"  {'Sell-side' if is_sellside else 'Buy-side'}  ·  {client}")
            add_log(f"  {sector}  ·  {sub_sector}  ·  {geography}")
            add_log(f"  {len(per_cat_caps)} categories  ·  ≈{sum(per_cat_caps.values())} companies")
            add_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            # ── Phase 1: Strategy (already done — just display it) ────────────
            add_log(f"\n[1/4] Mapping strategy  ✓  ({len(strategy['categories'])} categories)")
            for c in strategy["categories"]:
                add_log(f"     • {c['name']}  →  {per_cat_caps.get(c['name'], default_cap)} companies")

            # ── Phase 2: Discovery ────────────────────────────────────────────
            add_log(f"\n[2/4] Building universe…")
            discovered = discover_companies(
                strategy["categories"], inp,
                on_progress=add_log,
                per_cat_caps=per_cat_caps,
            )
            total_disc = sum(len(v) for v in discovered.values())
            # Save discovered companies as a mid-run checkpoint
            st.session_state.discovered_checkpoint = discovered
            add_log(f"\n  ✓ Discovery done  —  {total_disc} companies across {len(discovered)} categories")

            # ── Phase 3: Enrichment ───────────────────────────────────────────
            add_log(f"\n[3/4] Enriching {total_disc} companies…")
            enriched = enrich_all(
                discovered, inp,
                on_progress=add_log,
                on_company_done=_save_partial,
            )
            total_enr = sum(len(v) for v in enriched.values())
            add_log(f"\n  ✓ Enrichment done  —  {total_enr} companies")

            # ── Phase 4: Excel ────────────────────────────────────────────────
            add_log(f"\n[4/4] Writing Excel…")
            class _Q(io.StringIO):
                def write(self, s): return super().write(s)
            with contextlib.redirect_stdout(_Q()):
                generate_excel(strategy, enriched, inp, tmp_path)
            add_log(f"     ↳ Snapshot sheet  ✓")
            add_log(f"     ↳ {len(enriched)} mapping sheets  ✓")
            add_log(f"     ↳ Decision makers sheet  ✓")

            with open(tmp_path, "rb") as f:
                excel_bytes = f.read()
            os.unlink(tmp_path)

            st.session_state.excel_bytes    = excel_bytes
            st.session_state.excel_filename = filename

            add_log(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            add_log(f"  DONE  ·  {total_enr} companies  ·  {len(enriched)} categories")
            add_log(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            download_area.download_button(
                label="Download Excel",
                data=excel_bytes,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_final",
            )

        except Exception as e:
            add_log(f"\n[ERROR] {e}")
            st.error(f"Something went wrong: {e}")
