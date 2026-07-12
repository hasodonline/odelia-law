/*
 * ============================================================
 *  Analytics & conversion tracking — lawodelia.co.il
 *  Fill in the two IDs below once they exist, redeploy, done.
 *    1) GA4 Measurement ID  → from Google Analytics (Admin → Data streams)
 *    2) Google Ads conversion → from Ads (Goals → Conversions → the "call/lead" action)
 *  Until filled, this file is inert (no errors, no tracking).
 * ============================================================
 */
var GA_MEASUREMENT_ID = "G-VTQ9HQ301F";        // GA4 property "lawodelia.co.il"
var ADS_CONVERSION = { id: "", label: "" };    // e.g. { id: "AW-123456789", label: "AbC-D_efG" }

(function () {
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { dataLayer.push(arguments); };
  gtag("js", new Date());

  if (GA_MEASUREMENT_ID) {
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_MEASUREMENT_ID;
    document.head.appendChild(s);
    gtag("config", GA_MEASUREMENT_ID);
  }
  if (ADS_CONVERSION.id) gtag("config", ADS_CONVERSION.id);

  // Fire a lead conversion on phone / WhatsApp / form contact
  function fireLead(method) {
    gtag("event", "generate_lead", { method: method });
    if (ADS_CONVERSION.id && ADS_CONVERSION.label) {
      gtag("event", "conversion", { send_to: ADS_CONVERSION.id + "/" + ADS_CONVERSION.label });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('a[href^="tel:"]').forEach(function (a) {
      a.addEventListener("click", function () { fireLead("phone"); });
    });
    document.querySelectorAll('a[href*="wa.me"], a[href*="whatsapp"]').forEach(function (a) {
      a.addEventListener("click", function () { fireLead("whatsapp"); });
    });
    var form = document.getElementById("contactForm");
    if (form) form.addEventListener("submit", function () { fireLead("form"); });
  });
})();
