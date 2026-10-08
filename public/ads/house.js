/* ===========================================================================
   HOUSE ADS — the only file you need to edit to change what runs in the slots.

   No ad network involved. Each slot draws from the list below; if a slot has
   more than one creative, one is picked at random on each page view.

   TO SWAP IN A REAL BANNER
   ------------------------
   1. Drop the image into public/images/ads/  (PNG, JPG, SVG or GIF)
   2. Edit the matching entry below: set "img", "width", "height", "href" and
      "alt". Width and height must be the creative's real pixel size — they're
      what stops the page jumping as the image loads.
   3. Set SHOW_LABEL to true once these are real ads rather than placeholders.

   Nothing else changes: no templates, no regeneration, no deploy step beyond
   committing the file.

   Slots and their standard sizes:
     leaderboard  728x90   (320x50 on phones, via the "mobile" key)
     incontent    300x250
     footer       300x250
     rail         300x600  (only shows on screens 1200px and wider)

   Leave a slot's list empty — []  — and that slot collapses to nothing
   instead of showing a placeholder.
   =========================================================================== */

var HOUSE_ADS = {
  leaderboard: [
    {
      img: "/images/ads/placeholder-728x90.svg",
      width: 728,
      height: 90,
      alt: "Ad space",
      // href: "https://example.com/your-landing-page",
      mobile: { img: "/images/ads/placeholder-320x50.svg", width: 320, height: 50 }
    }
  ],

  incontent: [
    {
      img: "/images/ads/placeholder-300x250.svg",
      width: 300,
      height: 250,
      alt: "Ad space"
      // href: "https://example.com/your-landing-page",
    }
  ],

  footer: [
    {
      img: "/images/ads/placeholder-300x250.svg",
      width: 300,
      height: 250,
      alt: "Ad space"
      // href: "https://example.com/your-landing-page",
    }
  ],

  rail: [
    {
      img: "/images/ads/placeholder-300x600.svg",
      width: 300,
      height: 600,
      alt: "Ad space"
      // href: "https://example.com/your-landing-page",
    }
  ]
};

// Show the small "Advertisement" label above each slot. Off while these are
// placeholders (labelling a grey placeholder as an ad is just confusing);
// turn it on when real paid creative runs.
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

    // Phones get the small creative when one is supplied, so the image served
    // matches the height the stylesheet reserved.
    var creative = (window.innerWidth < 768 && ad.mobile) ? ad.mobile : ad;
    if (!creative || !creative.img) return slot.setFilled(false);

    var img = document.createElement("img");
    img.src = creative.img;
    img.width = creative.width;
    img.height = creative.height;
    img.alt = ad.alt || "";
    img.decoding = "async";
    // The leaderboard is above the fold and already gated by slots.js; the rest
    // only render once near the viewport, so native lazy loading is redundant
    // for them but harmless and helps if a creative is heavy.
    img.loading = slot.element.getAttribute("data-ad-eager") === "1" ? "eager" : "lazy";
    img.style.cssText = "max-width:100%;height:auto;display:block;border:0";

    if (ad.href) {
      var a = document.createElement("a");
      a.href = ad.href;
      // rel="sponsored" is what search engines expect on a paid placement.
      a.rel = "sponsored noopener";
      if (ad.newTab !== false) a.target = "_blank";
      a.appendChild(img);
      mount.appendChild(a);
    } else {
      mount.appendChild(img);
    }
  }
};
