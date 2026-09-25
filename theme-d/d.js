/* Theme D — behaviour. No dependencies; every feature works without it too
   (comparisons fall back to two photos side by side). */
(() => {
  "use strict";
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const el = (tag, cls, html) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html) n.innerHTML = html;
    return n;
  };

  /* Menu ------------------------------------------------------------------ */
  const menuBtn = $(".hdr__menu"), menu = $("#menu");
  if (menuBtn && menu) {
    const set = open => {
      menuBtn.setAttribute("aria-expanded", String(open));
      menu.hidden = !open;
      document.body.classList.toggle("lock", open);
    };
    menuBtn.addEventListener("click", () => set(menu.hidden));
    $$("a", menu).forEach(a => a.addEventListener("click", () => set(false)));
    document.addEventListener("keydown", e => {
      if (e.key === "Escape" && !menu.hidden) { set(false); menuBtn.focus(); }
    });
  }

  /* Before / after ---------------------------------------------------------
     A real range input sits over the photos, so dragging, clicking and the
     arrow keys all work and screen readers get a proper slider. */
  const KNOB = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 6-5 6 5 6M15 6l5 6-5 6"/></svg>';

  const setView = (ba, mode) => {
    $(".ba__frame", ba).classList.toggle("is-split", mode === "split");
    $$("[data-view]", ba).forEach(b => b.setAttribute("aria-pressed", String(b.dataset.view === mode)));
  };

  $$("[data-ba]").forEach(frame => {
    const before = $("[data-before]", frame), after = $("[data-after]", frame);
    if (!before || !after) return;
    const label = frame.dataset.label || "this project";

    const paneA = el("div", "ba__pane ba__pane--a"); paneA.dataset.tag = "After"; paneA.append(after);
    const paneB = el("div", "ba__pane ba__pane--b"); paneB.dataset.tag = "Before"; paneB.append(before);
    const range = Object.assign(document.createElement("input"), {
      type: "range", className: "ba__range", min: 0, max: 100, step: 0.5, value: 50,
    });
    range.setAttribute("aria-label", `Before and after of ${label}`);
    const line = el("div", "ba__line", `<span class="ba__knob">${KNOB}</span>`);
    line.setAttribute("aria-hidden", "true");

    frame.replaceChildren(paneA, paneB,
      el("span", "ba__tag ba__tag--b", "Before"), el("span", "ba__tag ba__tag--a", "After"),
      range, line);
    frame.classList.add("is-on");

    const apply = () => {
      frame.style.setProperty("--pos", `${range.value}%`);
      range.setAttribute("aria-valuetext", `${Math.round(range.value)}% showing before`);
    };
    range.addEventListener("input", apply);
    apply();

    const ba = frame.closest(".ba");
    const bar = $(".ba__bar", ba);
    if (bar) {
      const toggle = el("div", "ba__toggle",
        '<button type="button" data-view="slide" aria-pressed="true">Slider</button>' +
        '<button type="button" data-view="split" aria-pressed="false">Side by side</button>');
      toggle.setAttribute("role", "group");
      toggle.setAttribute("aria-label", "Show comparison as");
      toggle.addEventListener("click", e => {
        const b = e.target.closest("[data-view]");
        if (b) setView(ba, b.dataset.view);
      });
      bar.append(toggle);
    }
  });

  $$("[data-view-all]").forEach(btn => btn.addEventListener("click", () => {
    const mode = btn.dataset.viewAll;
    $$(".ba").forEach(ba => setView(ba, mode));
    $$("[data-view-all]").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.viewAll === mode)));
  }));

  /* Project filters ----------------------------------------------------- */
  const filters = $("[data-filters]");
  if (filters) {
    const works = $$(".work[data-category]");
    const count = $("[data-count]");
    const apply = key => {
      let n = 0;
      works.forEach(w => { const on = key === "all" || w.dataset.category === key; w.hidden = !on; n += on; });
      $$("[data-filter]", filters).forEach(b => b.setAttribute("aria-pressed", String(b.dataset.filter === key)));
      if (count) count.textContent = `${n} project${n === 1 ? "" : "s"}`;
      history.replaceState(null, "", key === "all" ? location.pathname : `?filter=${key}`);
    };
    filters.addEventListener("click", e => {
      const b = e.target.closest("[data-filter]");
      if (b) apply(b.dataset.filter);
    });
    const want = new URLSearchParams(location.search).get("filter");
    apply(want && $(`[data-filter="${want}"]`, filters) ? want : "all");
  }

  /* Estimate form -------------------------------------------------------
     Set data-endpoint to a real form handler (Formspree, Netlify Forms…).
     Until then it validates, then says plainly that nothing was sent. */
  const form = $("[data-form]");
  if (form) {
    const status = $(".form__status", form);
    const want = new URLSearchParams(location.search).get("service");
    const svc = $('select[name="service"]', form);
    if (want && svc && $(`option[value="${want}"]`, svc)) svc.value = want;

    const check = f => {
      const input = $("input, select, textarea", f);
      const err = $(".f__err", f);
      if (!input || !input.required) return true;
      const v = input.value.trim();
      let msg = "";
      if (!v) msg = "Required.";
      else if (input.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) msg = "Check the email address.";
      else if (input.type === "tel" && v.replace(/\D/g, "").length < 10) msg = "A 10-digit phone number, please.";
      f.classList.toggle("has-err", !!msg);
      input.toggleAttribute("aria-invalid", !!msg);
      if (err) err.textContent = msg;
      return !msg;
    };

    $$(".f", form).forEach(f => {
      const input = $("input, select, textarea", f);
      if (input) input.addEventListener("input", () => { if (f.classList.contains("has-err")) check(f); });
    });

    form.addEventListener("submit", async e => {
      e.preventDefault();
      status.hidden = true;
      const bad = $$(".f", form).filter(f => !check(f));
      if (bad.length) { $("input, select, textarea", bad[0]).focus(); return; }

      const btn = $('button[type="submit"]', form);
      const label = btn.textContent;
      btn.disabled = true; btn.textContent = "Sending…";
      const done = (state, msg) => {
        btn.disabled = false; btn.textContent = label;
        status.hidden = false; status.dataset.state = state; status.textContent = msg;
      };

      const endpoint = form.dataset.endpoint || "";
      if (!endpoint || endpoint.includes("REPLACE")) {
        setTimeout(() => {
          done("ok", "Thanks — that looks right. (Preview: no form endpoint is connected yet, so nothing was actually sent.)");
          form.reset();
        }, 500);
        return;
      }
      try {
        const r = await fetch(endpoint, { method: "POST", headers: { Accept: "application/json" }, body: new FormData(form) });
        if (!r.ok) throw new Error(r.status);
        done("ok", "Thanks — we've got it and will reply within one business day.");
        form.reset();
      } catch {
        done("err", "That didn't send. Please call (555) 014-2300 and we'll take the details by phone.");
      }
    });
  }

  /* Mobile call bar, once the opening photograph has scrolled away --------- */
  const bar = $(".callbar"), top = $(".hero") || $(".phead");
  if (bar) {
    const onScroll = () => bar.classList.toggle("is-on", scrollY > (top ? top.offsetHeight * 0.7 : 400));
    addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  $$("[data-year]").forEach(n => { n.textContent = new Date().getFullYear(); });
})();
