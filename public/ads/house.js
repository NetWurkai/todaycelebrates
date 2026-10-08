/* ===========================================================================
   HOUSE ADS — the only file you need to edit to change what runs in the slots.

   No ad network. Each slot draws from the list below; if a slot has more than
   one creative, one is picked at random per page view.

   TWO KINDS OF CREATIVE
   ---------------------
   HTML5 banner (type: "html")   an ad folder with its own index.html, served
                                 in an iframe. Handles its own click-through
                                 via the clickTag inside that index.html.
   Image        (no type)        a plain image, optionally wrapped in a link.

   TO CHANGE WHAT RUNS
   -------------------
   HTML5: drop the unzipped banner folder into public/ads/<campaign>/<size>/
          and point "src" at it. Set the click-through by editing the clickTag
          line near the top of that banner's own index.html.
   Image: drop the file into public/images/ads/ and set "img" + "href".

   Either way: width and height must be the creative's real pixel size. They're
   what stops the page jumping as it loads.

   Nothing else changes — no template edits, no regenerating the site's ~2,800
   pages, no deploy step beyond committing the file.

   Slots and their standard sizes:
     leaderboard  728x90   (320x50 on phones, via the "mobile" key)
     incontent    300x250
     footer       300x250
     rail         300x600  (only shows on screens 1200px and wider)

   Leave a slot's list empty — []  — and that slot collapses to nothing.
   =========================================================================== */

var HOUSE_ADS = {
  leaderboard: [
    {
      type: "html",
      src: "/ads/podiq/728x90/",
      width: 728,
      height: 90,
      alt: "PodIQ — launch your podcast",
      mobile: { type: "html", src: "/ads/podiq/320x50/", width: 320, height: 50 }
    }
  ],

  incontent: [
    {
      type: "html",
      src: "/ads/podiq/300x250/",
      width: 300,
      height: 250,
      alt: "PodIQ — launch your podcast"
    }
  ],

  footer: [
    {
      type: "html",
      src: "/ads/podiq/300x250/",
      width: 300,
      height: 250,
      alt: "PodIQ — launch your podcast"
    }
  ],

  rail: [
    {
      type: "html",
      src: "/ads/podiq/300x600/",
      width: 300,
      height: 600,
      alt: "PodIQ — launch your podcast"
    }
  ]
};

// Show the small "Advertisement" label above each slot. These are house ads
// for Jay's own product rather than sold inventory, so it's off; turn it on
// (together with ADS_LABELLED in generate.py) when third-party paid creative
// runs.
var SHOW_LABEL = false;

/* --------------------------------------------------------------------------
   Below here is the wiring. You shouldn't need to change it.
   -------------------------------------------------------------------------- */

window.TC_ADS = {
  label: SHOW_LABEL,

  fill: function (mount, slot) {
    var list = HOUSE_ADS[slot.name];
    if (!list || !list.length) {
      // Nothing booked for this position — collapse it.
      return slot.setFilled(false);
    }

    var ad = list.length === 1 ? list[0] : list[Math.floor(Math.random() * list.length)];

    // Phones get the small creative when one is supplied, so what's served
    // matches the height the stylesheet reserved. 768px is also where ads.css
    // stops widening the leaderboard slot to fit a 728px banner.
    var creative = (window.innerWidth < 768 && ad.mobile) ? ad.mobile : ad;
    if (!creative) return slot.setFilled(false);

    var eager = slot.element.getAttribute("data-ad-eager") === "1";
    var node;

    if (creative.type === "html") {
      if (!creative.src) return slot.setFilled(false);
      node = document.createElement("iframe");
      node.src = creative.src;
      node.title = ad.alt || "Advertisement";
      node.setAttribute("scrolling", "no");
      node.setAttribute("frameborder", "0");
      // Opaque-origin sandbox: the creative can run its own script and open
      // its click-through, but cannot reach this page's DOM, cookies or
      // storage. Fonts inside it are then cross-origin, which is why
      // public/_headers sends Access-Control-Allow-Origin for /ads/*/shared/fonts/.
      node.setAttribute(
        "sandbox",
        "allow-scripts allow-popups allow-popups-to-escape-sandbox"
      );
    } else {
      if (!creative.img) return slot.setFilled(false);
      node = document.createElement("img");
      node.src = creative.img;
      node.alt = ad.alt || "";
      node.decoding = "async";
    }

    node.width = creative.width;
    node.height = creative.height;
    node.loading = eager ? "eager" : "lazy";
    node.style.cssText = "display:block;border:0;max-width:100%";

    // An image creative can carry its own link; an HTML5 banner does its own
    // click handling via clickTag, so never wrap one in an anchor.
    if (creative.type !== "html" && ad.href) {
      var a = document.createElement("a");
      a.href = ad.href;
      // rel="sponsored" is what search engines expect on a paid placement.
      a.rel = "sponsored noopener";
      if (ad.newTab !== false) a.target = "_blank";
      a.appendChild(node);
      mount.appendChild(a);
    } else {
      mount.appendChild(node);
    }
  }
};
