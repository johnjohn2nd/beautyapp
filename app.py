import hashlib
import requests
import streamlit as st
from datetime import datetime, timezone

# ── Constants ──────────────────────────────────────────────────────────────────
API_DEFAULT = "https://script.google.com/macros/s/REPLACE_WITH_YOUR_/exec"

COMMIT_DEADLINE_UTC = datetime(2026, 11, 30, 22, 59, 59, tzinfo=timezone.utc)
REVEAL_OPEN_UTC     = datetime(2025, 10, 21, 22,  0,  0, tzinfo=timezone.utc)

# ── Helpers ────────────────────────────────────────────────────────────────────
def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Beauty Contest – Commit & Reveal", page_icon="🔐")
st.title("🔐 Beauty Contest – Commit & Reveal")

# ── API URL ────────────────────────────────────────────────────────────────────
with st.expander("⚙️ API Settings", expanded=False):
    api_url = st.text_input("API URL", value=API_DEFAULT)

st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_commit, tab_reveal = st.tabs(["📤 Commit", "📬 Reveal"])

# ══════════════════════════════════════════════════════════════════════════════
# COMMIT TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_commit:
    st.subheader("Commit Phase")
    st.caption(f"Deadline (Paris): **30 Nov 2026 23:59:59** · (UTC): 30 Nov 2026 22:59:59")

    current = now_utc()
    if current > COMMIT_DEADLINE_UTC:
        st.error("⛔ The commit window is **closed**. Deadline has passed.")
    else:
        remaining = COMMIT_DEADLINE_UTC - current
        st.success(f"✅ Commit window is **open** — {remaining.days}d {remaining.seconds // 3600}h remaining.")

        uni_id  = st.text_input("Your NEOMA ID", key="c_uni")
        number  = st.number_input("Your guess (0–100)", min_value=0, max_value=100,
                                  step=1, key="c_number")
        nonce   = st.text_input("Secret nonce (keep it safe!)", type="password", key="c_nonce")

        if st.button("🔒 Generate hash & Commit", type="primary"):
            if not uni_id:
                st.warning("Please enter your NEOMA ID.")
            elif not nonce:
                st.warning("Please enter a nonce.")
            else:
                preimage    = f"{uni_id}|{int(number)}|{nonce}"
                commit_hash = sha256(preimage)

                st.success("Hash generated!")
                st.code(commit_hash, language=None)

                with st.expander("🔑 Your preimage (save this!)"):
                    st.code(preimage, language=None)
                    st.caption("You will need to re-enter your ID, number, and nonce exactly during the reveal phase.")

                with st.spinner("Sending to server…"):
                    try:
                        payload = {"kind": "commit", "uni_id": uni_id, "commit": commit_hash}
                        r = requests.post(api_url, json=payload, timeout=15)
                        st.info(f"Server response ({r.status_code}): {r.text}")
                    except Exception as e:
                        st.error(f"Network error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# REVEAL TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_reveal:
    st.subheader("Reveal Phase")
    st.caption(f"Opens (Paris): **22 Oct 2025 00:00:00** · (UTC): 21 Oct 2025 22:00:00")

    current = now_utc()
    if current < REVEAL_OPEN_UTC:
        st.error("⛔ The reveal window is **not open yet**.")
    else:
        st.success("✅ Reveal window is **open**.")

        uni_id_r = st.text_input("Your NEOMA ID", key="r_uni")
        number_r = st.number_input("Your number (0–100)", min_value=0, max_value=100,
                                   step=1, key="r_number")
        nonce_r  = st.text_input("Your secret nonce", type="password", key="r_nonce")

        if st.button("📬 Reveal", type="primary"):
            if not uni_id_r:
                st.warning("Please enter your NEOMA ID.")
            elif not nonce_r:
                st.warning("Please enter your nonce.")
            else:
                with st.spinner("Sending to server…"):
                    try:
                        payload = {
                            "kind":   "reveal",
                            "uni_id": uni_id_r,
                            "number": int(number_r),
                            "nonce":  nonce_r,
                        }
                        r = requests.post(api_url, json=payload, timeout=15)
                        st.info(f"Server response ({r.status_code}): {r.text}")
                    except Exception as e:
                        st.error(f"Network error: {e}")
