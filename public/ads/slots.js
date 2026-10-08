/* ---------------------------------------------------------------------------
   Today Celebrates — display ad slot runtime.

   Provider-agnostic on purpose. This file finds the slots, decides when each
   one should load, reserves its space and labels it. It does NOT know about
   Google Ad Manager, AdSense, or any particular network — that goes in one
   place (see "WIRING UP A PROVIDER" at the bottom), so swapping networks or
   going direct-sold never means editing page templates or regenerating the
   site's ~2,800 pages.

   Until a provider is configured this script does nothing at all: no space
   reserved, no requests, no visible change. That is deliberate — the slots can
   ship now and be switched on whenever the inventory is worth selling.

   To wire up Google Ad Manager, AdSense or a direct-sold creative, see the
   "Display ad slots" section of scripts/README.md.
--------------------------------------------------------------------------- */
(function () {
  "use strict";

  // Standard IAB sizes per slot name. Passed to the provider so it can map
  // them to its own ad-unit definitions.
  var SIZES = {
    leaderboard: [[728, 90], [320, 50]],
    incontent: [[300, 250]],
    footer: [[300, 250]],
    rail: [[300, 600]]
  };

  var provider = window.TC_ADS;
  if (!provider || typeof provider.fill !== "function") {
    // No provider configured. Leave every slot collapsed and invisible.
    return;
  }

  // NOTE: the .ads-enabled / .ads-labelled classes are NOT added here. They are
  // baked into <html> at build time by generate.py (ADS_ENABLED / ADS_LABELLED),
  // because adding them from this deferred script happens after first paint and
  // reflows the whole page when the slots appear. This script only fills slots.
  if (!document.documentElement.classList.contains("ads-enabled")) return;

  function render(el) {
    if (el.getAttribute("data-ad-filled")) return;
    el.setAttribute("data-ad-filled", "1");

    var name = el.getAttribute("data-ad-slot");

    // Paid placements should be labelled as such; a provider can opt out while
    // it's only running placeholders by setting TC_ADS.label = false.
    if (provider.label !== false) {
      var label = document.createElement("span");
      label.className = "ad-label";
      label.textContent = "Advertisement";
      el.appendChild(label);
    }

    var mount = document.createElement("div");
    mount.className = "ad-mount";
    el.appendChild(mount);

    try {
      provider.fill(mount, {
        name: name,
        sizes: SIZES[name] || [],
        element: el,
        // Call this with false when the slot comes back unfilled, so the
        // reserved space collapses instead of leaving a labelled hole.
        setFilled: function (didFill) {
          if (didFill === false) el.setAttribute("data-ad-empty", "1");
        }
      });
    } catch (err) {
      // An ad failure must never take the page down with it.
      el.setAttribute("data-ad-empty", "1");
      if (window.console && console.warn) {
        console.warn("[ads] slot " + name + " failed:", err);
      }
    }
  }

  var slots = Array.prototype.slice.call(
    document.querySelectorAll("[data-ad-slot]")
  );

  // Above-the-fold slots load immediately; everything else waits until it is
  // near the viewport, so a creative far down the page costs nothing to a
  // visitor who never scrolls to it.
  var deferred = [];
  slots.forEach(function (el) {
    if (el.getAttribute("data-ad-eager") === "1") {
      render(el);
    } else {
      deferred.push(el);
    }
  });

  if (!deferred.length) return;

  if (typeof IntersectionObserver === "function") {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          observer.unobserve(entry.target);
          render(entry.target);
        });
      },
      { rootMargin: "300px 0px" }
    );
    deferred.forEach(function (el) {
      observer.observe(el);
    });
  } else {
    // No IntersectionObserver (very old browsers): just render them.
    deferred.forEach(render);
  }
})();
