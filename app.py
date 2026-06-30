"""Automap — Streamlit UI for Accomplir Advisors M&A Mapping Tool"""

import io
import os
import tempfile
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

from automap import (
    MOTIVATIONS, COMPANY_TYPES, COUNT_OPTIONS,
    generate_strategy, discover_companies, enrich_all, generate_excel,
)

st.set_page_config(
    page_title="Automap · Accomplir",
    page_icon="🍧",
    layout="wide",
)

# ── Original pink melting-sorbet illustration (SVG) ─────────────────────────────
SORBET_SVG = """
<svg viewBox="0 0 480 380" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="240" cy="350" rx="120" ry="16" fill="#FFD9E6"/>

  <path d="M150 188 Q160 250 180 320 Q200 345 240 345 Q280 345 300 320 Q320 250 330 188 Z" fill="#FF8FAE"/>
  <path d="M170 230 Q165 270 178 300 Q183 290 182 250 Z" fill="#FF6F96" opacity="0.7"/>
  <path d="M300 235 Q308 268 296 298 Q291 286 293 248 Z" fill="#FF6F96" opacity="0.7"/>

  <path d="M210 300 Q205 325 213 340 Q221 330 218 302 Z" fill="#FF5C8A"/>
  <path d="M255 305 Q252 328 261 338 Q268 326 264 306 Z" fill="#FF5C8A"/>
  <path d="M236 312 Q231 332 238 344 Q246 333 242 313 Z" fill="#FF7AA0"/>

  <circle cx="240" cy="178" r="86" fill="#FF5C8A"/>
  <circle cx="240" cy="178" r="86" fill="url(#g1)" opacity="0.35"/>

  <circle cx="240" cy="96" r="72" fill="#FF85A8"/>
  <circle cx="240" cy="96" r="72" fill="url(#g1)" opacity="0.3"/>

  <circle cx="240" cy="34" r="50" fill="#FFB3C6"/>

  <ellipse cx="206" cy="20" rx="16" ry="22" fill="#FFE0EA" opacity="0.85"/>
  <ellipse cx="208" cy="98" rx="20" ry="28" fill="#FFC2D6" opacity="0.55"/>
  <ellipse cx="206" cy="170" rx="24" ry="34" fill="#FF85A8" opacity="0.45"/>

  <path d="M240 -10 Q224 4 222 18 Q224 30 240 32 Q256 30 258 18 Q256 4 240 -10 Z" fill="#7FB88D"/>
  <path d="M240 -8 L240 22" stroke="#5C9468" stroke-width="2" fill="none"/>

  <defs>
    <radialGradient id="g1" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>
  </defs>
</svg>
"""

# ── Log line colorizer ─────────────────────────────────────────────────────────
def _colorize(line: str) -> str:
    s = line.rstrip()
    if not s.strip():
        return "<br>"
    esc = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if "━" in s or "═" in s:
        return f'<span style="color:#5c4452;">{esc}</span>'
    if s.lstrip().startswith("[") and "/4]" in s:
        return f'<span style="color:#FF85A8;font-weight:700;">{esc}</span>'
    if "[ERROR]" in s:
        return f'<span style="color:#FFB3C6;text-decoration:underline;">{esc}</span>'
    if "→" in s or "DONE" in s or "✓" in s:
        return f'<span style="color:#fff;">{esc}</span>'
    if s.startswith("     •"):
        return f'<span style="color:#9b7d8a;">{esc}</span>'
    return f'<span style="color:#cbb6c0;">{esc}</span>'

# ── CSS injection ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:ital,opsz,wght@0,12..96,400..800;1,12..96,400..800&family=Fraunces:ital,opsz,wght@1,9..144,500..700&family=Inter:wght@300;400;500;600;700&display=swap');

*, html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
}}

.stApp {{
    background: #FFFCF6 !important;
}}

.block-container {{
    padding: 0 2.5rem 2rem !important;
    max-width: 100% !important;
    position: relative;
    z-index: 1;
}}

/* ── Hero ── */
.hero {{
    text-align: center;
    padding: 36px 0 8px;
}}
.hero-illus {{
    width: 220px;
    max-width: 60vw;
    margin: 0 auto;
    filter: drop-shadow(0 10px 16px rgba(0,0,0,0.08));
}}
.hero-title-wrap {{
    position: relative;
    display: inline-block;
}}
.hero-title {{
    font-family: 'Fraunces', serif;
    font-optical-sizing: auto;
    font-variation-settings: "opsz" 144, "SOFT" 60, "WONK" 1;
    font-style: italic;
    font-size: 120px;
    font-weight: 600;
    letter-spacing: -0.01em;
    line-height: 0.95;
    color: #5E2A50;
    margin-top: 4px;
    transform: skewX(-5deg);
    display: inline-block;
}}
.title-drip {{
    position: absolute;
    right: 2%;
    bottom: -34px;
    width: 30px;
    pointer-events: none;
}}
.title-rule {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
    margin-top: 24px;
}}
.title-rule .ln {{
    width: 60px;
    height: 1px;
    background: #C9A98E;
}}
.title-rule .dot {{
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #C9A98E;
}}
.hero-tag {{
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-size: 15px;
    font-weight: 500;
    color: #8a6f78;
    margin-top: 14px;
    letter-spacing: 0.01em;
}}
.hero-sub {{
    font-size: 11px;
    color: #B89A85;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-top: 6px;
}}

/* ── Scroll-fixed ice-cream drips ── */
.drip {{
    position: fixed;
    z-index: 0;
    pointer-events: none;
}}

/* ── Section labels ── */
.sec {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: #2A2A2A;
    text-transform: uppercase;
    border-bottom: 2px solid #EDEDED;
    padding-bottom: 8px;
    margin: 30px 0 16px;
}}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: #FAFAFA !important;
    border: 1.5px solid #E5E5E5 !important;
    border-radius: 14px !important;
    color: #2A2A2A !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: #FF8FAE !important;
    box-shadow: 0 0 0 4px rgba(255,143,174,0.1) !important;
    outline: none !important;
}}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {{
    color: #b5b5b5 !important;
}}

/* ── Labels ── */
.stTextInput label, .stTextArea label {{
    color: #6b6b6b !important;
    font-size: 11.5px !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
}}

/* ── Radio ── */
div[data-testid="stRadioGroup"] > div > label {{
    color: #2A2A2A !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
}}

/* ── Checkbox ── */
.stCheckbox label span {{
    color: #2A2A2A !important;
    font-size: 12.5px !important;
}}
.stCheckbox > label {{
    color: #6b6b6b !important;
    font-size: 11px !important;
}}

/* ── Sub-label ── */
.sub-lbl {{
    font-size: 11.5px;
    font-weight: 600;
    letter-spacing: 0.03em;
    color: #6b6b6b;
    margin: 16px 0 8px;
}}

/* ── Run button ── */
div[data-testid="stButton"] > button {{
    background: #2A2A2A !important;
    color: #fff !important;
    border: none !important;
    border-radius: 14px !important;
    font-family: 'Bricolage Grotesque', sans-serif !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    padding: 15px 32px !important;
    width: 100% !important;
    margin-top: 14px !important;
    transition: opacity 0.18s ease !important;
}}
div[data-testid="stButton"] > button:hover {{
    opacity: 0.85 !important;
}}

/* ── Download button ── */
div[data-testid="stDownloadButton"] > button {{
    background: #fff !important;
    color: #2A2A2A !important;
    border: 1.5px solid #2A2A2A !important;
    border-radius: 14px !important;
    font-family: 'Bricolage Grotesque', sans-serif !important;
    font-size: 13.5px !important;
    font-weight: 700 !important;
    padding: 12px 24px !important;
    width: 100% !important;
}}
div[data-testid="stDownloadButton"] > button:hover {{
    background: #FAFAFA !important;
}}

/* ── Log terminal ── */
.log-box {{
    background: #1d1d1d;
    border-radius: 18px;
    padding: 22px 24px;
    font-family: 'Inter', monospace;
    font-size: 12px;
    line-height: 1.9;
    max-height: 520px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
}}
.log-box::-webkit-scrollbar {{ width: 4px; }}
.log-box::-webkit-scrollbar-track {{ background: transparent; }}
.log-box::-webkit-scrollbar-thumb {{ background: #FF8FAE; border-radius: 2px; }}

/* ── Misc ── */
hr {{ border-color: #EDEDED !important; }}
[data-testid="stHorizontalBlock"] {{ gap: 3rem; }}
div[data-testid="stAlert"] {{ border-radius: 12px !important; }}
#MainMenu, footer, header {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ── Fixed, melty ice-cream drips along the edges (stay put while the page scrolls) ──
# Three irregular blob paths — uneven tails, asymmetric lumps, not a clean teardrop
_BLOB_A = "M20 2 C30 1 40 10 40 22 C40 32 34 36 32 44 C30 52 35 58 31 64 C29 68 25 65 24 58 C23 52 19 56 17 63 C15 69 9 65 11 56 C13 48 5 44 4 33 C2 20 9 3 20 2 Z"
_BLOB_B = "M22 0 C34 -1 43 11 41 24 C39 35 30 38 27 48 C25 56 29 64 26 72 C24 77 19 73 19 64 C19 54 14 50 10 40 C5 28 9 13 22 0 Z"
_BLOB_C = "M18 3 C26 -2 36 4 38 14 C40 24 33 26 36 34 C39 42 32 44 33 52 C34 60 27 64 24 58 C21 52 24 46 18 42 C10 38 6 28 8 18 C10 9 12 6 18 3 Z"
_BLOBS  = [_BLOB_A, _BLOB_B, _BLOB_C]

def _drip(side: str, top: str, size: int, color: str, blob: int = 0, opacity: float = 1.0) -> str:
    # Most of the shape sits off-screen — only a melty sliver pokes into the page, clear of text
    edge = f"left:-{size*0.62:.0f}px;" if side == "left" else f"right:-{size*0.62:.0f}px;"
    return f"""<div class="drip" style="{edge} top:{top}; width:{size}px; height:{size*1.85:.0f}px; opacity:{opacity};">
        <svg viewBox="0 0 44 78" xmlns="http://www.w3.org/2000/svg">
          <path d="{_BLOBS[blob % 3]}" fill="{color}"/>
          <ellipse cx="15" cy="18" rx="4" ry="6" fill="#ffffff" opacity="0.3"/>
        </svg>
    </div>"""

DRIPS = "".join([
    _drip("left",  "8%",  50, "#FF8FAE", blob=0, opacity=0.6),
    _drip("left",  "34%", 64, "#9BD8FF", blob=1, opacity=0.5),
    _drip("left",  "62%", 42, "#FFB3C6", blob=2, opacity=0.55),
    _drip("left",  "86%", 56, "#BFE9FF", blob=0, opacity=0.45),
    _drip("right", "16%", 58, "#9BD8FF", blob=2, opacity=0.5),
    _drip("right", "44%", 44, "#FF5C8A", blob=1, opacity=0.5),
    _drip("right", "70%", 66, "#FFB3C6", blob=0, opacity=0.42),
    _drip("right", "92%", 40, "#BFE9FF", blob=2, opacity=0.55),
])
st.markdown(DRIPS, unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
TITLE_DRIP = f"""<svg class="title-drip" viewBox="0 0 44 78" xmlns="http://www.w3.org/2000/svg">
  <path d="{_BLOB_B}" fill="#5E2A50"/>
  <ellipse cx="15" cy="18" rx="4" ry="6" fill="#ffffff" opacity="0.25"/>
</svg>"""

st.markdown(f"""
<div class="hero">
  <div class="hero-illus">{SORBET_SVG}</div>
  <div class="hero-title-wrap">
    <div class="hero-title">Sorbet</div>
    {TITLE_DRIP}
  </div>
  <div class="hero-tag">Automated M&amp;A mapping, by Accomplir Advisors</div>
  <div class="title-rule"><span class="ln"></span><span class="dot"></span><span class="ln"></span></div>
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

    client = st.text_input("Client / company name", placeholder="e.g. Cessna Lifeline Veterinary Healthcare Pvt Ltd")
    role   = "company being sold" if is_sellside else "acquirer"
    company_desc = st.text_area(
        f"Describe the company ({role})",
        placeholder="Products, scale, geography, any special context — paste freely",
        height=100,
    )

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
        '<span style="font-weight:400;color:#D9A8B8;font-size:11px;text-transform:none;">— all optional</span></div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        target_geography = st.text_input("Target geography",     placeholder="Pan-India / South India")
        revenue_range    = st.text_input("Revenue range",         placeholder=">100 Cr  or  50–500 Cr")
    with c2:
        specific_attrs   = st.text_input("Must-have attributes",  placeholder="manufacturing / CRISIL rated")
        what_looking_for = st.text_input("Specifically seeking",  placeholder="Eastern India / R&D")

    st.markdown('<div class="sub-lbl">Company types to include</div>', unsafe_allow_html=True)
    type_cols = st.columns(2)
    company_types = []
    for i, ct in enumerate(COMPANY_TYPES):
        if type_cols[i % 2].checkbox(ct, value=True, key=f"ct_{i}"):
            company_types.append(ct)

    st.markdown('<div class="sec">Volume</div>', unsafe_allow_html=True)
    count_labels = [v[0] for v in COUNT_OPTIONS.values()]
    count_choice = st.radio("Companies to map", count_labels, index=2, label_visibility="collapsed")
    per_cat_cap  = next(cap for lbl, cap in COUNT_OPTIONS.values() if lbl == count_choice)

    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("Run Mapping")

# ── Output ────────────────────────────────────────────────────────────────────
with col_out:

    st.markdown('<div class="sec">Progress</div>', unsafe_allow_html=True)
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

    if run_btn:
        errors = []
        if not client.strip():        errors.append("Client name is required.")
        if not company_desc.strip():  errors.append("Company description is required.")
        if not sector.strip():        errors.append("Sector is required.")
        if not sub_sector.strip():    errors.append("Sub-sector is required.")
        if not geography.strip():     errors.append("Client geography is required.")
        if not motivations:           errors.append("Select at least one M&A motivation.")
        if not company_types:         errors.append("Select at least one company type.")

        if errors:
            for e in errors:
                st.error(e)
            st.stop()

        st.session_state.log_lines   = []
        st.session_state.excel_bytes = None
        download_area.empty()

        inp = {
            "is_sellside":      is_sellside,
            "client":           client.strip(),
            "company_desc":     company_desc.strip(),
            "sector":           sector.strip(),
            "sub_sector":       sub_sector.strip(),
            "geography":        geography.strip(),
            "motivations":      motivations,
            "target_geography": target_geography.strip() or "Pan-India",
            "revenue_range":    revenue_range.strip()    or "No filter",
            "specific_attrs":   specific_attrs.strip()   or "None",
            "what_looking_for": what_looking_for.strip() or "None",
            "company_types":    company_types,
            "per_cat_cap":      per_cat_cap,
            "count_label":      count_choice,
            "date":             datetime.today().strftime("%d-%b-%y"),
        }

        import contextlib

        add_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        add_log(f"  {'Sell-side' if is_sellside else 'Buy-side'}  /  {client}")
        add_log(f"  {sector}  /  {sub_sector}  /  {geography}")
        add_log(f"  Volume: {count_choice}")
        add_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        class _Quiet(io.StringIO):
            def write(self, s):
                return super().write(s)

        try:
            add_log("\n[1/4] Generating mapping strategy...")
            cap = _Quiet()
            with contextlib.redirect_stdout(cap):
                strategy = generate_strategy(inp)
            add_log(f"  → {len(strategy['categories'])} categories identified")
            for c in strategy["categories"]:
                add_log(f"     • {c['name']}")

            add_log("\n[2/4] Building company universe...")
            cap = _Quiet()
            with contextlib.redirect_stdout(cap):
                discovered = discover_companies(strategy["categories"], inp)
            total_disc = sum(len(v) for v in discovered.values())
            add_log(f"  → {total_disc} companies identified")

            add_log(f"\n[3/4] Enriching {total_disc} companies...")
            cap = _Quiet()
            with contextlib.redirect_stdout(cap):
                enriched = enrich_all(discovered, inp)
            add_log("  → Enrichment complete")

            add_log("\n[4/4] Generating Excel...")
            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
                tmp_path = tmp.name
            with contextlib.redirect_stdout(cap):
                generate_excel(strategy, enriched, inp, tmp_path)

            with open(tmp_path, "rb") as f:
                excel_bytes = f.read()
            os.unlink(tmp_path)

            date_tag = datetime.today().strftime("%d%b%y")
            filename = f"Accomplir - {client} - Mapping - {date_tag}.xlsx"
            st.session_state.excel_bytes    = excel_bytes
            st.session_state.excel_filename = filename

            total = sum(len(v) for v in enriched.values())
            add_log(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            add_log(f"  DONE  /  {total} companies  /  {len(enriched)} categories")
            add_log(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            download_area.download_button(
                label="Download Excel",
                data=excel_bytes,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except Exception as e:
            add_log(f"\n[ERROR] {e}")
            st.error(f"Something went wrong: {e}")
