/* =============================================================================
   American Restoration Tech — site behaviour
   Vanilla JS, no dependencies. Every feature degrades gracefully without it.
   ========================================================================== */
(function () {
  "use strict";

  var $  = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  /* --- Sticky header shadow ---------------------------------------------- */
  var header = $(".site-header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-stuck", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* --- Mobile drawer ------------------------------------------------------ */
  var toggle = $(".nav__toggle");
  var drawer = $(".drawer");
  if (toggle && drawer) {
    var setDrawer = function (open) {
      toggle.setAttribute("aria-expanded", String(open));
      drawer.classList.toggle("is-open", open);
      drawer.setAttribute("aria-hidden", String(!open));
      document.body.classList.toggle("is-locked", open);
    };
    setDrawer(false);
    toggle.addEventListener("click", function () {
      setDrawer(toggle.getAttribute("aria-expanded") !== "true");
    });
    $$("a", drawer).forEach(function (a) {
      a.addEventListener("click", function () { setDrawer(false); });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setDrawer(false);
        toggle.focus();
      }
    });
  }

  /* --- Before / after comparison ------------------------------------------
     Authoring contract — keep the markup minimal:

       <figure class="compare-block">
         <div class="compare" data-compare data-label="Kitchen rebuild">
           <img data-compare-before src="…-before.jpg" alt="Before: …">
           <img data-compare-after  src="…-after.jpg"  alt="After: …">
         </div>
         <div class="compare-bar"><figcaption>Bethesda, MD</figcaption></div>
       </figure>

     This script builds the slider, labels, drag handle and the
     slider / side-by-side toggle. With JavaScript off the two photos simply
     render next to each other, which is still a perfectly good experience.
     ---------------------------------------------------------------------- */
  var KNOB = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">' +
             '<path d="m9 6-5 6 5 6M15 6l5 6-5 6" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  function el(tag, className, html) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (html) node.innerHTML = html;
    return node;
  }

  function buildCompare(node) {
    var before = $("[data-compare-before]", node);
    var after = $("[data-compare-after]", node);
    if (!before || !after) return null;

    var label = node.getAttribute("data-label") || "this project";

    var paneAfter = el("div", "compare__pane compare__pane--after");
    var paneBefore = el("div", "compare__pane compare__pane--before");
    paneAfter.setAttribute("data-tag", "After");
    paneBefore.setAttribute("data-tag", "Before");
    paneAfter.appendChild(after);
    paneBefore.appendChild(before);

    var panes = el("div", "compare__panes");
    panes.appendChild(paneAfter);
    panes.appendChild(paneBefore);

    var tagBefore = el("span", "compare__tag compare__tag--before", "Before");
    var tagAfter = el("span", "compare__tag compare__tag--after", "After");

    var range = el("input", "compare__range");
    range.type = "range";
    range.min = "0";
    range.max = "100";
    range.step = "0.5";
    range.value = node.getAttribute("data-start") || "50";
    range.setAttribute("aria-label", "Reveal the before or after photo of " + label);

    var divider = el("div", "compare__divider", '<span class="compare__knob">' + KNOB + "</span>");
    divider.setAttribute("aria-hidden", "true");

    node.textContent = "";
    node.appendChild(panes);
    node.appendChild(tagBefore);
    node.appendChild(tagAfter);
    node.appendChild(range);
    node.appendChild(divider);
    node.classList.add("is-ready");

    var engaged = false;

    var apply = function () {
      node.style.setProperty("--pos", range.value + "%");
      range.setAttribute("aria-valuetext", Math.round(range.value) + "% before photo shown");
    };
    range.addEventListener("input", function () { engaged = true; apply(); });
    node.addEventListener("pointerdown", function () { engaged = true; });
    range.addEventListener("keydown", function () { engaged = true; });
    apply();

    // A small nudge on first hover so the handle reads as draggable. It must
    // yield the instant the visitor touches the control, or it fights their
    // drag for the length of the animation.
    var teased = false;
    node.addEventListener("pointerenter", function () {
      if (teased || engaged || node.classList.contains("is-split")) return;
      teased = true;
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
      var start = parseFloat(range.value);
      var t0 = performance.now();
      (function step(t) {
        if (engaged) { apply(); return; }
        var p = Math.min((t - t0) / 640, 1);
        node.style.setProperty("--pos", (start + Math.sin(p * Math.PI) * 7) + "%");
        if (p < 1) requestAnimationFrame(step); else apply();
      })(t0);
    });

    return node;
  }

  function setView(block, mode) {
    var compare = $(".compare", block);
    if (!compare) return;
    compare.classList.toggle("is-split", mode === "split");
    $$("[data-view]", block).forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-view") === mode));
    });
  }

  function addToggle(block) {
    var bar = $(".compare-bar", block);
    if (!bar || $("[data-view]", bar)) return;
    var group = el("div", "compare-toggle",
      '<button type="button" data-view="slider" aria-pressed="true">Slider</button>' +
      '<button type="button" data-view="split" aria-pressed="false">Side by side</button>');
    group.setAttribute("role", "group");
    group.setAttribute("aria-label", "Comparison view");
    bar.appendChild(group);
    $$("[data-view]", group).forEach(function (btn) {
      btn.addEventListener("click", function () { setView(block, btn.getAttribute("data-view")); });
    });
  }

  $$("[data-compare]").forEach(function (node) {
    if (!buildCompare(node)) return;
    var block = node.closest(".compare-block");
    if (block) addToggle(block);
  });

  // Page-level control: flip every comparison on the page at once.
  $$("[data-view-all]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var mode = btn.getAttribute("data-view-all");
      $$(".compare-block").forEach(function (block) { setView(block, mode); });
      $$("[data-view-all]").forEach(function (b) {
        b.setAttribute("aria-pressed", String(b.getAttribute("data-view-all") === mode));
      });
    });
  });

  /* --- Project filtering --------------------------------------------------- */
  var filterBar = $("[data-filters]");
  if (filterBar) {
    var projects = $$("[data-category]");
    var count = $("[data-result-count]");

    var applyFilter = function (value) {
      var shown = 0;
      projects.forEach(function (p) {
        var match = value === "all" || p.getAttribute("data-category") === value;
        p.hidden = !match;
        if (match) shown++;
      });
      $$(".filter", filterBar).forEach(function (b) {
        b.setAttribute("aria-pressed", String(b.getAttribute("data-filter") === value));
      });
      if (count) {
        count.textContent = shown + (shown === 1 ? " project" : " projects");
      }
      if (history.replaceState) {
        history.replaceState(null, "", value === "all" ? location.pathname : "?filter=" + value);
      }
    };

    $$(".filter", filterBar).forEach(function (btn) {
      btn.addEventListener("click", function () {
        applyFilter(btn.getAttribute("data-filter"));
      });
    });

    var preset = new URLSearchParams(location.search).get("filter");
    applyFilter(preset && $('.filter[data-filter="' + preset + '"]', filterBar) ? preset : "all");
  }

  /* --- Contact form -------------------------------------------------------
     Set data-endpoint on the <form> to a real handler (Formspree, Netlify
     Forms, your own script). Until then the form validates and shows a
     preview confirmation so the flow can be demonstrated.
     ---------------------------------------------------------------------- */
  var form = $("[data-contact-form]");
  if (form) {
    var status = $(".form__status", form);

    // Pre-select the service when arriving from a /services link.
    var wanted = new URLSearchParams(location.search).get("service");
    var serviceField = $("#service", form);
    if (wanted && serviceField && $('option[value="' + wanted + '"]', serviceField)) {
      serviceField.value = wanted;
    }

    var showError = function (field, message) {
      field.classList.add("has-error");
      var slot = $(".error", field);
      if (slot) slot.textContent = message;
      var input = $("input, select, textarea", field);
      if (input) input.setAttribute("aria-invalid", "true");
    };

    var clearError = function (field) {
      field.classList.remove("has-error");
      var slot = $(".error", field);
      if (slot) slot.textContent = "";
      var input = $("input, select, textarea", field);
      if (input) input.removeAttribute("aria-invalid");
    };

    var validate = function () {
      var firstBad = null;
      $$(".field", form).forEach(function (field) {
        var input = $("input[required], select[required], textarea[required]", field);
        clearError(field);
        if (!input) return;
        var value = (input.value || "").trim();
        if (!value) {
          showError(field, "This field is required.");
        } else if (input.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value)) {
          showError(field, "Enter a valid email address.");
        } else if (input.type === "tel" && value.replace(/\D/g, "").length < 10) {
          showError(field, "Enter a 10-digit phone number.");
        }
        if (field.classList.contains("has-error") && !firstBad) firstBad = input;
      });
      return firstBad;
    };

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (status) { status.hidden = true; status.removeAttribute("data-state"); }

      var bad = validate();
      if (bad) {
        bad.focus();
        bad.scrollIntoView({ block: "center", behavior: "smooth" });
        return;
      }

      var submitBtn = $('button[type="submit"]', form);
      var endpoint = form.getAttribute("data-endpoint") || "";
      var finish = function (state, message) {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = submitBtn.dataset.label; }
        if (!status) return;
        status.hidden = false;
        status.setAttribute("data-state", state);
        status.textContent = message;
        status.scrollIntoView({ block: "center", behavior: "smooth" });
      };

      if (submitBtn) {
        submitBtn.dataset.label = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = "Sending…";
      }

      // No live endpoint configured yet — demonstrate the success state.
      if (!endpoint || endpoint.indexOf("REPLACE") !== -1) {
        window.setTimeout(function () {
          finish("success",
            "Thanks — your request has been received. (Demo mode: no form endpoint is " +
            "configured yet, so nothing was actually sent.) We reply to every request within one business day.");
          form.reset();
        }, 600);
        return;
      }

      fetch(endpoint, {
        method: "POST",
        headers: { Accept: "application/json" },
        body: new FormData(form)
      })
        .then(function (res) {
          if (!res.ok) throw new Error("Request failed");
          finish("success", "Thanks — your request has been received. We reply to every request within one business day.");
          form.reset();
        })
        .catch(function () {
          finish("error", "Something went wrong sending your request. Please call (555) 014-2300 and we'll take the details over the phone.");
        });
    });

    $$("input, select, textarea", form).forEach(function (input) {
      input.addEventListener("input", function () {
        var field = input.closest(".field");
        if (field && field.classList.contains("has-error")) clearError(field);
      });
    });
  }

  /* --- Sticky mobile call bar ---------------------------------------------
     Appears once the hero (and its buttons) have scrolled away, so the phone
     number is never more than one tap from anywhere on the page.
     ---------------------------------------------------------------------- */
  var callbar = $(".callbar");
  if (callbar) {
    var trigger = $(".hero") || $(".page-head");
    var showAfter = function () {
      var cut = trigger ? trigger.offsetHeight * 0.75 : 400;
      callbar.classList.toggle("is-visible", window.scrollY > cut);
    };
    showAfter();
    window.addEventListener("scroll", showAfter, { passive: true });
  }

  /* --- Scroll reveal ------------------------------------------------------- */
  var targets = $$("[data-reveal]");
  if (targets.length && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        io.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    targets.forEach(function (t) { io.observe(t); });
  } else {
    targets.forEach(function (t) { t.classList.add("is-visible"); });
  }

  /* --- Footer year --------------------------------------------------------- */
  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
