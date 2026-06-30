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
    page_icon="■",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Courier+Prime:ital,wght@0,400;0,700;1,400&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Courier Prime', 'Courier New', monospace !important;
}

/* ── Background ── */
.stApp {
    background: #ffffff !important;
}

/* ── Remove Streamlit padding ── */
.block-container {
    padding: 0 2.5rem 2rem !important;
    max-width: 100% !important;
}

/* ── Header ── */
.hdr {
    border-bottom: 2px solid #000;
    padding: 28px 0 14px;
    margin-bottom: 0;
}
.hdr-title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.38em;
    text-transform: uppercase;
    color: #000;
}
.hdr-meta {
    font-size: 11px;
    color: #000;
    letter-spacing: 0.12em;
    margin-top: 3px;
}

/* ── Section labels ── */
.sec {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.32em;
    color: #000;
    text-transform: uppercase;
    border-bottom: 1px solid #000;
    padding-bottom: 5px;
    margin: 28px 0 14px;
}

/* ── All text inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid #000 !important;
    border-radius: 0 !important;
    color: #000 !important;
    font-family: 'Courier Prime', monospace !important;
    font-size: 13px !important;
    padding: 6px 0 6px 0 !important;
    box-shadow: none !important;
    outline: none !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-bottom: 2px solid #000 !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #999 !important;
    font-style: italic !important;
}

/* ── Labels ── */
.stTextInput label, .stTextArea label {
    color: #000 !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
}

/* ── Radio ── */
div[data-testid="stRadioGroup"] > div > label {
    color: #000 !important;
    font-size: 12px !important;
    font-family: 'Courier Prime', monospace !important;
}

/* ── Checkbox ── */
.stCheckbox label span {
    color: #000 !important;
    font-size: 12px !important;
    font-family: 'Courier Prime', monospace !important;
}
.stCheckbox > label {
    color: #000 !important;
    font-size: 10px !important;
}

/* ── Sub-label (optional fields) ── */
.sub-lbl {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #000;
    margin: 14px 0 6px;
}

/* ── Run button ── */
div[data-testid="stButton"] > button {
    background: #000 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'Courier Prime', monospace !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 0.32em !important;
    text-transform: uppercase !important;
    padding: 14px 32px !important;
    width: 100% !important;
    margin-top: 12px !important;
    transition: opacity 0.15s ease !important;
}
div[data-testid="stButton"] > button:hover {
    opacity: 0.82 !important;
}

/* ── Download button ── */
div[data-testid="stDownloadButton"] > button {
    background: #fff !important;
    color: #000 !important;
    border: 1px solid #000 !important;
    border-radius: 0 !important;
    font-family: 'Courier Prime', monospace !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    padding: 12px 24px !important;
    width: 100% !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: #000 !important;
    color: #fff !important;
}

/* ── Log terminal ── */
.log-box {
    background: #000;
    border: none;
    padding: 20px 22px;
    font-family: 'Courier Prime', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.85;
    max-height: 520px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
}
.log-box::-webkit-scrollbar { width: 2px; }
.log-box::-webkit-scrollbar-track { background: #000; }
.log-box::-webkit-scrollbar-thumb { background: #555; }

/* ── Divider between cols ── */
.col-divider {
    border-left: 1px solid #000;
    height: 100%;
}

/* ── Misc ── */
hr { border-color: #000 !important; margin: 0 !important; }
[data-testid="stHorizontalBlock"] { gap: 3rem; }
div[data-testid="stAlert"] { border-radius: 0 !important; font-family: 'Courier Prime', monospace !important; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Log colorizer — white on black terminal ────────────────────────────────────
def _colorize(line: str) -> str:
    s = line.rstrip()
    if not s.strip():
        return "<br>"
    esc = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if "━" in s or "═" in s:
        return f'<span style="color:#444;">{esc}</span>'
    if s.lstrip().startswith("[") and "/4]" in s:
        return f'<span style="color:#fff;font-weight:700;">{esc}</span>'
    if "[ERROR]" in s:
        return f'<span style="color:#ccc;text-decoration:underline;">{esc}</span>'
    if "→" in s or "DONE" in s or "✓" in s:
        return f'<span style="color:#fff;">{esc}</span>'
    if s.startswith("     •"):
        return f'<span style="color:#666;">{esc}</span>'
    return f'<span style="color:#aaa;">{esc}</span>'

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hdr">
  <span class="hdr-title">Automap</span>
  <span class="hdr-meta" style="margin-left:32px;">Accomplir Advisors &nbsp;/&nbsp; M&A Intelligence &nbsp;/&nbsp; {datetime.today().strftime("%d %b %Y")}</span>
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

    client = st.text_input("Client / company name", placeholder="e.g. ChetNet Hosiery Private Limited")
    role   = "company being sold" if is_sellside else "acquirer"
    company_desc = st.text_area(
        f"Describe the company ({role})",
        placeholder="Products, scale, geography, any special context — paste freely",
        height=100,
    )

    c1, c2 = st.columns(2)
    with c1:
        sector     = st.text_input("Sector",          placeholder="Apparel / Textiles")
    with c2:
        sub_sector = st.text_input("Sub-sector",      placeholder="Hosiery & Innerwear")

    geography = st.text_input("Client geography", placeholder="Ludhiana, Punjab")

    st.markdown('<div class="sec">M&A Motivations</div>', unsafe_allow_html=True)
    motivation_cols = st.columns(2)
    motivations = []
    for i, m in enumerate(MOTIVATIONS):
        if motivation_cols[i % 2].checkbox(m, key=f"mot_{i}"):
            motivations.append(m)

    st.markdown(
        '<div class="sec">Target Filters '
        '<span style="font-weight:400;letter-spacing:0.06em;font-size:9px;">— all optional</span></div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        target_geography = st.text_input("Target geography",  placeholder="Pan-India / South India")
        revenue_range    = st.text_input("Revenue range",     placeholder=">100 Cr  or  50–500 Cr")
    with c2:
        specific_attrs   = st.text_input("Must-have attributes", placeholder="manufacturing / CRISIL rated")
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
