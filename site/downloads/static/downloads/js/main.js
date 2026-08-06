(function () {
  function detectPlatform() {
    var platform = navigator.platform || "";
    var ua = navigator.userAgent || "";
    if (/Win/i.test(platform) || /Windows/i.test(ua)) return "windows";
    if (/Mac/i.test(platform) || /Macintosh/i.test(ua)) return "macos";
    if (/Linux/i.test(platform) || /Linux/i.test(ua)) return "linux";
    return null;
  }

  document.addEventListener("DOMContentLoaded", function () {
    // Progressive enhancement: the hero button starts as a plain "jump to
    // the download section" link (see index.html) and only becomes a
    // direct download link once we can tell what OS the visitor is on and
    // confirm that channel actually has a build for it.
    var detected = detectPlatform();
    var heroButton = document.querySelector("[data-hero-download]");
    if (detected && heroButton) {
      var target = document.querySelector('[data-platform-link="' + detected + '"][data-channel="prod"]');
      if (target) {
        heroButton.setAttribute("href", target.getAttribute("href"));
        heroButton.textContent = "Download for " + target.getAttribute("data-platform-label");
      }
    }

    var tabs = document.querySelectorAll("[data-channel-tab]");
    var panels = document.querySelectorAll("[data-channel-panel]");
    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        var channel = tab.getAttribute("data-channel-tab");
        tabs.forEach(function (t) {
          t.classList.toggle("active", t === tab);
        });
        panels.forEach(function (p) {
          p.classList.toggle("active", p.getAttribute("data-channel-panel") === channel);
        });
      });
    });
  });
})();
