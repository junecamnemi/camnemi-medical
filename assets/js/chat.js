/* ==========================================================================
   Camnemi Medical Service — live chat widget
   Visitor side of a visitor <-> Telegram bridge.

   Storage + realtime: Supabase (anon/publishable key, safe for the browser).
   A session id is minted per visitor and kept in localStorage so the same
   person keeps their thread across reloads. Agent replies arrive over
   Supabase Realtime and render live. No login required.
   ========================================================================== */
(function () {
  "use strict";

  var SUPABASE_URL = "https://zjdvzpylxazfbazioxto.supabase.co";
  var SUPABASE_KEY = "sb_publishable_KFjRXn0mQ8-a38MiOc3ppQ_X5KzqgbL";
  var LS_KEY = "camnemi_chat_session";

  // Loaded lazily so the widget adds nothing to the critical path.
  var SB_CDN = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.js";

  var sb = null;          // supabase client
  var sessionId = null;   // current chat session uuid
  var channel = null;     // realtime subscription
  var seenIds = {};       // dedupe rendered messages
  var opened = false;

  /* ---- build DOM -------------------------------------------------------- */
  var root = document.createElement("div");
  root.className = "cchat";
  root.innerHTML =
    '<button class="cchat__fab" type="button" aria-label="Chat with us" aria-expanded="false">' +
      '<i class="ri-chat-3-line" aria-hidden="true"></i>' +
      '<span class="cchat__fab-txt">Chat</span>' +
      '<span class="cchat__badge" hidden>1</span>' +
    '</button>' +
    '<section class="cchat__panel" role="dialog" aria-label="Chat with Camnemi Medical Service" hidden>' +
      '<header class="cchat__head">' +
        '<div class="cchat__head-id">' +
          '<span class="cchat__dot" aria-hidden="true"></span>' +
          '<div><strong>Camnemi Medical Service</strong><span class="cchat__sub">We usually reply within minutes</span></div>' +
        '</div>' +
        '<button class="cchat__close" type="button" aria-label="Close chat">&times;</button>' +
      '</header>' +
      '<div class="cchat__intro" data-intro>' +
        '<p class="cchat__intro-t">Hi! 👋 How can we help?</p>' +
        '<p class="cchat__intro-d">Leave your name and email so our coordinator can follow up, then send your message.</p>' +
        '<div class="cchat__field"><input type="text" data-name placeholder="Your name" autocomplete="name"></div>' +
        '<div class="cchat__field"><input type="email" data-email placeholder="Email" autocomplete="email"></div>' +
        '<button class="btn btn--primary btn--block cchat__start" type="button">Start chat</button>' +
        '<p class="cchat__err" data-err hidden></p>' +
      '</div>' +
      '<div class="cchat__log" data-log hidden aria-live="polite"></div>' +
      '<form class="cchat__composer" data-composer hidden>' +
        '<input type="text" data-input placeholder="Type a message…" autocomplete="off" aria-label="Message">' +
        '<button class="cchat__send" type="submit" aria-label="Send"><i class="ri-send-plane-2-fill" aria-hidden="true"></i></button>' +
      '</form>' +
    '</section>';
  document.body.appendChild(root);

  var fab = root.querySelector(".cchat__fab");
  var panel = root.querySelector(".cchat__panel");
  var badge = root.querySelector(".cchat__badge");
  var introBox = root.querySelector("[data-intro]");
  var logBox = root.querySelector("[data-log]");
  var composer = root.querySelector("[data-composer]");
  var input = root.querySelector("[data-input]");
  var nameEl = root.querySelector("[data-name]");
  var emailEl = root.querySelector("[data-email]");
  var errEl = root.querySelector("[data-err]");
  var startBtn = root.querySelector(".cchat__start");

  /* ---- helpers ---------------------------------------------------------- */
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function addBubble(msg) {
    if (msg.id && seenIds[msg.id]) return;
    if (msg.id) seenIds[msg.id] = true;
    var el = document.createElement("div");
    el.className = "cchat__msg cchat__msg--" + (msg.sender === "agent" ? "agent" : "me");
    el.innerHTML = '<span class="cchat__bubble">' + esc(msg.body) + "</span>";
    logBox.appendChild(el);
    logBox.scrollTop = logBox.scrollHeight;
  }

  function showThread() {
    introBox.hidden = true;
    logBox.hidden = false;
    composer.hidden = false;
    input.focus();
  }

  function loadSupabase() {
    return new Promise(function (resolve, reject) {
      if (window.supabase && window.supabase.createClient) return resolve();
      var s = document.createElement("script");
      s.src = SB_CDN;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    }).then(function () {
      if (!sb) sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
    });
  }

  function subscribe() {
    if (channel || !sessionId) return;
    channel = sb
      .channel("chat:" + sessionId)
      .on("postgres_changes",
        { event: "INSERT", schema: "public", table: "chat_messages", filter: "session_id=eq." + sessionId },
        function (payload) {
          var m = payload.new;
          if (m.sender === "agent") {
            addBubble(m);
            if (!opened) bumpBadge();
          }
        })
      .subscribe();
  }

  function bumpBadge() {
    var n = parseInt(badge.textContent || "0", 10) + 1;
    badge.textContent = String(n);
    badge.hidden = false;
  }

  function clearBadge() {
    badge.hidden = true;
    badge.textContent = "0";
  }

  /* ---- load history for a returning visitor ----------------------------- */
  function hydrate() {
    return sb.from("chat_messages")
      .select("id,sender,body,created_at")
      .eq("session_id", sessionId)
      .order("created_at", { ascending: true })
      .then(function (res) {
        if (res.error || !res.data) return;
        if (res.data.length) showThread();
        res.data.forEach(addBubble);
      });
  }

  /* ---- open / close ----------------------------------------------------- */
  function openPanel() {
    panel.hidden = false;
    fab.setAttribute("aria-expanded", "true");
    opened = true;
    clearBadge();
    loadSupabase().then(function () {
      sessionId = sessionId || localStorage.getItem(LS_KEY);
      if (sessionId) {
        showThread();
        hydrate();
        subscribe();
      } else {
        nameEl.focus();
      }
    });
  }
  function closePanel() {
    panel.hidden = true;
    fab.setAttribute("aria-expanded", "false");
    opened = false;
  }

  fab.addEventListener("click", function () { panel.hidden ? openPanel() : closePanel(); });
  root.querySelector(".cchat__close").addEventListener("click", closePanel);

  /* ---- start a new session --------------------------------------------- */
  startBtn.addEventListener("click", function () {
    var nm = nameEl.value.trim();
    var em = emailEl.value.trim();
    errEl.hidden = true;
    if (!nm) { errEl.textContent = "Please enter your name."; errEl.hidden = false; nameEl.focus(); return; }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(em)) {
      errEl.textContent = "Please enter a valid email."; errEl.hidden = false; emailEl.focus(); return;
    }
    startBtn.disabled = true;
    sb.from("chat_sessions").insert({
      visitor_name: nm, visitor_email: em,
      page_url: location.href, user_agent: navigator.userAgent.slice(0, 300)
    }).select("id").single().then(function (res) {
      startBtn.disabled = false;
      if (res.error || !res.data) { errEl.textContent = "Could not start chat. Please email medical@camnemi.com."; errEl.hidden = false; return; }
      sessionId = res.data.id;
      localStorage.setItem(LS_KEY, sessionId);
      showThread();
      subscribe();
    });
  });

  /* ---- send a message --------------------------------------------------- */
  composer.addEventListener("submit", function (e) {
    e.preventDefault();
    var body = input.value.trim();
    if (!body || !sessionId) return;
    input.value = "";
    var optimistic = { sender: "visitor", body: body };
    addBubble(optimistic);
    sb.from("chat_messages").insert({ session_id: sessionId, sender: "visitor", body: body })
      .then(function (res) {
        if (res.error) { addBubble({ sender: "agent", body: "⚠️ Message failed to send. Please try again or email medical@camnemi.com." }); }
      });
    // bump session activity so the agent side sorts it to the top
    sb.from("chat_sessions").update({ last_active: new Date().toISOString() }).eq("id", sessionId).then(function () {});
  });
})();
