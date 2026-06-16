/* =====================================================
   InternAI — Shared JS Utilities
   ===================================================== */

// ── Toggle password visibility ──────────────────────
function togglePassword(inputId, btn) {
  const input = document.getElementById(inputId);
  const isText = input.type === 'text';
  input.type = isText ? 'password' : 'text';
  btn.innerHTML = isText
    ? `<svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`
    : `<svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`;
}

// ── Password strength meter ──────────────────────────
const STRENGTH_COLORS = ['#ef4444', '#f97316', '#eab308', '#10a37f'];
const STRENGTH_LABELS = ['Weak', 'Fair', 'Good', 'Strong'];

function checkStrength(val, barId, labelId) {
  let score = 0;
  if (val.length >= 8) score++;
  if (/[A-Z]/.test(val)) score++;
  if (/[0-9]/.test(val)) score++;
  if (/[^A-Za-z0-9]/.test(val)) score++;

  for (let i = 1; i <= 4; i++) {
    const seg = document.getElementById(barId + i);
    if (seg) seg.style.background = i <= score ? STRENGTH_COLORS[score - 1] : 'var(--surface-2)';
  }

  const lbl = document.getElementById(labelId);
  if (lbl) {
    lbl.textContent = val.length === 0 ? '' : (STRENGTH_LABELS[score - 1] || 'Too short');
    lbl.style.color = score > 0 ? STRENGTH_COLORS[score - 1] : 'var(--text-muted)';
  }
}

// ── Alert helpers ────────────────────────────────────
function showAlert(id, msg, type = 'error') {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg;
  el.className = `alert alert-${type} visible`;
}
function hideAlert(id) {
  const el = document.getElementById(id);
  if (el) el.className = 'alert';
}

// ── Auto-resize textarea ─────────────────────────────
function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 180) + 'px';
}
