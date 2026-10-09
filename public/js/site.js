/* Today Celebrates — shared behaviour: share / copy link / add to calendar,
   search, date jump. Loaded with defer on every page. No dependencies.

   Everything here is progressive enhancement: the pages are complete without
   it (share-intent links are plain <a href>s), and nothing in this file changes
   layout on load, so it cannot cause layout shift. */
(function () {
  "use strict";

  function $(s, r) { return (r || document).querySelector(s); }

  /* ---------- toast ---------- */
  var toastEl = $("#toast"), toastTimer;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add("on");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("on"); }, 2200);
  }

  function absUrl(u) { return new URL(u, location.origin).href; }

  /* ---------- copy / share ---------- */
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).then(function () { toast("Link copied"); },
                                                      function () { fallbackCopy(text); });
    }
    fallbackCopy(text);
    return Promise.resolve();
  }
  function fallbackCopy(text) {
    var t = document.createElement("textarea");
    t.value = text; t.setAttribute("readonly", "");
    t.style.cssText = "position:fixed;top:0;left:0;opacity:0";
    document.body.appendChild(t); t.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) {}
    document.body.removeChild(t);
    toast(ok ? "Link copied" : "Copy failed — press and hold the address bar");
  }
  function share(ctx) {
    var url = absUrl(ctx.u), title = ctx.n;
    if (navigator.share) {
      navigator.share({ title: title, text: ctx.t || title, url: url }).catch(function (e) {
        if (e && e.name !== "AbortError") copyText(url);
      });
    } else {
      copyText(url);
    }
  }

  /* ---------- add to calendar (.ics), built in the browser ---------- */
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function icsEsc(s) { return String(s).replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\r?\n/g, "\\n"); }
  function addToCalendar(ctx) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(ctx.d || "");
    if (!m) return;
    var y = +m[1], mo = +m[2], d = +m[3];
    var end = new Date(Date.UTC(y, mo - 1, d + 1));
    var s = m[1] + m[2] + m[3];
    var e = end.getUTCFullYear() + pad(end.getUTCMonth() + 1) + pad(end.getUTCDate());
    var now = new Date();
    var stamp = now.getUTCFullYear() + pad(now.getUTCMonth() + 1) + pad(now.getUTCDate()) + "T" +
                pad(now.getUTCHours()) + pad(now.getUTCMinutes()) + pad(now.getUTCSeconds()) + "Z";
    var url = absUrl(ctx.u);
    var slug = (ctx.u.split("/").filter(Boolean).pop()) || "event";
    var lines = [
      "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Today Celebrates//Calendar//EN", "CALSCALE:GREGORIAN",
      "BEGIN:VEVENT", "UID:" + slug + "-" + s + "@todaycelebrates.com", "DTSTAMP:" + stamp,
      "DTSTART;VALUE=DATE:" + s, "DTEND;VALUE=DATE:" + e,
      "SUMMARY:" + icsEsc(ctx.n), "DESCRIPTION:" + icsEsc(url), "URL:" + url
    ];
    if (ctx.y === "1") lines.push("RRULE:FREQ=YEARLY");
    lines.push("TRANSP:TRANSPARENT", "END:VEVENT", "END:VCALENDAR");
    var blob = new Blob([lines.join("\r\n") + "\r\n"], { type: "text/calendar;charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = slug + ".ics";
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
    toast("Calendar file downloaded");
  }

  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest && ev.target.closest("[data-a]");
    if (!btn) return;
    var holder = btn.closest("[data-u]");
    if (!holder) return;
    var ctx = { u: holder.dataset.u, n: holder.dataset.n, d: holder.dataset.d, y: holder.dataset.y, t: holder.dataset.t };
    var a = btn.dataset.a;
    if (a === "copy") copyText(absUrl(ctx.u));
    else if (a === "share") share(ctx);
    else if (a === "ics") addToCalendar(ctx);
  });

  /* ---------- search ---------- */
  var q = $("#q"), box = $("#sres"), idx = null, loading = false, waiting = [], active = -1, hits = [];
  function loadIndex(cb) {
    if (idx) return cb();
    waiting.push(cb);
    if (loading) return;
    loading = true;
    fetch("/data/search.json").then(function (r) { return r.json(); }).then(function (j) {
      idx = j.map(function (e) { return { n: e[0], s: e[1], l: e[0].toLowerCase() }; });
    }).catch(function () { idx = []; }).then(function () {
      var w = waiting; waiting = []; w.forEach(function (f) { f(); });
    });
  }
  function closeBox() {
    if (!box) return;
    box.hidden = true; active = -1; q.setAttribute("aria-expanded", "false");
    q.removeAttribute("aria-activedescendant");
  }
  function esc(s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function render() {
    var v = q.value.trim().toLowerCase();
    if (v.length < 2) return closeBox();
    var starts = [], words = [], inner = [];
    for (var i = 0; i < idx.length; i++) {
      var p = idx[i].l.indexOf(v);
      if (p === 0) starts.push(idx[i]);
      else if (p > 0 && idx[i].l.charAt(p - 1) === " ") words.push(idx[i]);
      else if (p > 0) inner.push(idx[i]);
    }
    hits = starts.concat(words, inner).slice(0, 8);
    active = -1;
    box.innerHTML = hits.length
      ? hits.map(function (h, i) {
          return '<li role="presentation"><a role="option" id="sr' + i + '" href="/holiday/' + h.s + '/">' + esc(h.n) + "</a></li>";
        }).join("")
      : '<li class="none" role="presentation">No matches. Try a shorter word.</li>';
    box.hidden = false;
    q.setAttribute("aria-expanded", "true");
  }
  function mark(i) {
    var opts = box.querySelectorAll("a");
    for (var k = 0; k < opts.length; k++) opts[k].setAttribute("aria-selected", k === i ? "true" : "false");
    active = i;
    if (i >= 0) q.setAttribute("aria-activedescendant", "sr" + i); else q.removeAttribute("aria-activedescendant");
  }
  if (q && box) {
    q.addEventListener("focus", function () { loadIndex(function () {}); });
    q.addEventListener("input", function () { loadIndex(render); });
    q.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") { closeBox(); return; }
      if (box.hidden || !hits.length) return;
      if (ev.key === "ArrowDown") { ev.preventDefault(); mark(Math.min(active + 1, hits.length - 1)); }
      else if (ev.key === "ArrowUp") { ev.preventDefault(); mark(Math.max(active - 1, 0)); }
    });
    q.form.addEventListener("submit", function (ev) {
      // With JS the search never leaves the page: go to the chosen (or best) match.
      ev.preventDefault();
      if (!idx) { loadIndex(function () { render(); go(); }); return; }
      go();
    });
    document.addEventListener("click", function (ev) { if (!q.form.contains(ev.target)) closeBox(); });
  }
  function go() {
    var h = hits[active >= 0 ? active : 0];
    if (h) location.href = "/holiday/" + h.s + "/";
  }

  /* ---------- jump to date ---------- */
  var jump = $("#jump");
  if (jump) {
    jump.addEventListener("change", function () {
      var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(jump.value);
      if (!m) return;
      var key = +m[1] + "-" + +m[2] + "-" + +m[3];
      if (location.pathname === "/") location.hash = key; else location.href = "/#" + key;
    });
  }
})();
