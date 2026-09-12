/* ==========================================================================
   Camnemi Korea — site behaviour
   Vanilla JS, no dependencies. Everything degrades gracefully without it.
   ========================================================================== */
(function () {
  "use strict";

  var EMAIL = "medical@camnemi.com";

  /* --- 1. Mobile navigation --------------------------------------------- */
  var toggle = document.querySelector("[data-nav-toggle]");
  var nav = document.querySelector("[data-nav]");

  function closeNav() {
    if (!nav || !toggle) return;
    nav.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open menu");
  }

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) closeNav();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeNav();
    });
  }

  /* --- 2. Scroll spy: mark the section currently in view ---------------- */
  var navLinks = nav ? Array.prototype.slice.call(nav.querySelectorAll("a")) : [];
  var spyTargets = navLinks
    .map(function (a) {
      var id = (a.getAttribute("href") || "").replace(/^#/, "");
      var el = id ? document.getElementById(id) : null;
      return el ? { link: a, el: el } : null;
    })
    .filter(Boolean);

  if (spyTargets.length && "IntersectionObserver" in window) {
    var spy = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var match = spyTargets.find(function (t) { return t.el === entry.target; });
          if (!match) return;
          navLinks.forEach(function (a) { a.removeAttribute("aria-current"); });
          match.link.setAttribute("aria-current", "true");
        });
      },
      { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
    );
    spyTargets.forEach(function (t) { spy.observe(t.el); });
  }

  /* --- 3. Reveal on scroll (skipped when motion is reduced) -------------- */
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduce && "IntersectionObserver" in window) {
    var candidates = document.querySelectorAll(
      ".section-head, .card, .stat, .badge-card, .pkg, .proc, .spec, .callout, .split__media, .split__body, .includes, .table-wrap"
    );
    var reveal = new IntersectionObserver(
      function (entries, obs) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          obs.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.06 }
    );
    Array.prototype.forEach.call(candidates, function (el, i) {
      el.classList.add("reveal");
      el.style.transitionDelay = Math.min(i % 6, 4) * 60 + "ms";
      reveal.observe(el);
    });
  }

  /* --- 4. Inquiry form -> mail client ----------------------------------- */
  /* No backend and no third party: the form composes a mailto: so the
     visitor's own email app sends it to medical@camnemi.com. */
  var form = document.getElementById("contact-form");
  if (form) {
    var status = form.querySelector("[data-form-status]");

    function setStatus(msg, state) {
      if (!status) return;
      status.textContent = msg;
      if (state) status.setAttribute("data-state", state);
      else status.removeAttribute("data-state");
    }

    form.addEventListener("submit", function (event) {
      event.preventDefault();

      var name = form.elements.name;
      var email = form.elements.email;
      var phone = form.elements.phone;
      var interest = form.elements.interest;
      var message = form.elements.message;

      [name, email].forEach(function (el) {
        el.setAttribute("aria-invalid", el.value.trim() ? "false" : "true");
      });

      if (!name.value.trim()) {
        setStatus("Please enter your name.", "err");
        name.focus();
        return;
      }
      if (!email.value.trim() || email.value.indexOf("@") === -1) {
        setStatus("Please enter a valid email address.", "err");
        email.focus();
        return;
      }

      var lines = [
        "Name: " + name.value.trim(),
        "Email: " + email.value.trim(),
        "Phone: " + (phone.value.trim() || "-"),
        "Area of Interest: " + (interest.value || "-"),
        "",
        message.value.trim()
      ].join("\r\n");

      var href = "mailto:" + EMAIL +
        "?subject=" + encodeURIComponent("Camnemi Korea - Medical Inquiry") +
        "&body=" + encodeURIComponent(lines);

      window.location.href = href;
      setStatus("Your email app is opening with your inquiry. Send it to reach " + EMAIL + ".", "ok");
      form.reset();
      [name, email].forEach(function (el) { el.setAttribute("aria-invalid", "false"); });
    });

    form.addEventListener("input", function (e) {
      if (e.target.closest("input, textarea, select")) {
        e.target.setAttribute("aria-invalid", "false");
      }
    });
  }

  /* --- 5. Header elevation on scroll ------------------------------------ */
  var header = document.querySelector("[data-header]");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }
})();
