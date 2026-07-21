/**
 * Galtea Assistant — docs-site widget.
 *
 * Mintlify auto-includes any `.js` file in the content root on every page,
 * so this script runs everywhere without any docs.json wiring. Inclusion is
 * gated at build time by the SHOW_PLATFORM_ASSISTANT env var — when off,
 * `docs/scripts/run.py` deletes this file from `.build/` so the widget is
 * never served (see `gate_platform_assistant`).
 *
 * Renders a floating "Ask Val" command launcher — the brand mark in a
 * gradient chip, not a support bubble — matching the dashboard widget
 * (`AssistantWidget`). On click, mounts a sandboxed iframe
 * pointing at the dashboard's `/embed/assistant?embed=true` route — the same
 * React panel used by the authenticated dashboard widget. The iframe runs
 * `forceAnonymous=true` and `credentials: 'omit'`, so docs visitors stay
 * anonymous and no cookies cross the iframe boundary
 * (platform-assistant ADR 0004).
 */
(function () {
  "use strict";

  // Replaced at build time by docs/scripts/run.py from the DASHBOARD_URL env var
  // (defaults to https://platform.galtea.ai when unset).
  const DASHBOARD_URL = "https://dev.platform.galtea.ai";
  const ASSISTANT_PATH = "/embed/assistant?embed=true";

  if (window.__galteaAssistantMounted) return;
  window.__galteaAssistantMounted = true;

  // The angular Galtea mark (same symbol as the dashboard's GalteaMark), filled
  // dark so it stays legible on the bright soft-blue → lime chip in both themes.
  const MARK_SVG =
    '<svg viewBox="296 228 380 374" xmlns="http://www.w3.org/2000/svg"><path d="M667.221 395.232a4.775 4.775 0 0 1 4.773 4.772v33.199c0 1.109-.9 2.01-2.01 2.01-91.004 0-164.777 73.773-164.777 164.777 0 1.11-.901 2.009-2.01 2.01H468.09a4.774 4.774 0 0 1-4.774-4.773v-88.963l23.879-18.334a410.48 410.48 0 0 0 75.592-75.594l14.668-19.104h89.766ZM572.992 302.316a4.773 4.773 0 0 1 6.281.413l16.95 16.949a4.773 4.773 0 0 1 .41 6.281l-61.231 79.746a386.572 386.572 0 0 1-71.197 71.199l-79.748 61.231a4.773 4.773 0 0 1-6.281-.41l-16.949-16.95a4.772 4.772 0 0 1-.411-6.281l61.231-79.748a386.572 386.572 0 0 1 71.199-71.197l79.746-61.233ZM499.904 228.682a4.773 4.773 0 0 1 4.774 4.771v86.477l-25.996 19.959a410.438 410.438 0 0 0-75.592 75.592l-15.332 19.968h-86.985a4.774 4.774 0 0 1-4.773-4.773v-33.197c0-1.11.9-2.01 2.01-2.01 91.004 0 164.777-73.773 164.777-164.778a2.01 2.01 0 0 1 2.01-2.009h35.107Z"/></svg>';

  // Mintlify toggles `class="dark"` on <html> for its appearance switcher and
  // its system-preference resolver. We mirror that into the iframe so the
  // embedded React panel renders in the same mode the visitor is reading in.
  const currentDocsTheme = () =>
    document.documentElement.classList.contains("dark") ? "dark" : "light";
  const iframeSrc = () =>
    DASHBOARD_URL + ASSISTANT_PATH + "&theme=" + currentDocsTheme();

  const mount = () => {
    const styleEl = document.createElement("style");
    styleEl.textContent = `
				button.ga-launcher{position:fixed;right:24px;bottom:24px;z-index:2147483600;display:flex;align-items:center;gap:10px;padding:7px 14px 7px 7px;border:1px solid #ebebeb;background:#fbfbf9;border-radius:999px;cursor:pointer;box-shadow:0 8px 24px rgba(0,0,0,.10);transition:transform .18s cubic-bezier(.4,0,.2,1),box-shadow .3s;font-family:Geist,ui-sans-serif,system-ui,-apple-system,sans-serif}
				button.ga-launcher:hover{transform:translateY(-2px);box-shadow:0 0 8px 0 #a9cffe,0 0 18px 0 #c8f15f,0 10px 28px rgba(0,0,0,.14)}
				button.ga-launcher:focus-visible{outline:2px solid #c8f15f;outline-offset:2px}
				.ga-chip{width:34px;height:34px;border-radius:11px;display:grid;place-items:center;flex:none;background:linear-gradient(150deg,#a9cffe,#c8f15f);animation:ga-breathe 3.4s ease-in-out infinite}
				.ga-chip svg{width:19px;height:19px;fill:#171717}
				.ga-label{font-size:14px;font-weight:600;color:#171717;white-space:nowrap}
				@keyframes ga-breathe{0%,100%{box-shadow:0 0 0 0 rgba(200,241,95,0)}50%{box-shadow:0 0 12px 1px rgba(200,241,95,.55)}}
				@media (prefers-reduced-motion:reduce){.ga-chip{animation:none}button.ga-launcher{transition:none}}
				@media (max-width:520px){.ga-label{display:none}button.ga-launcher{padding:7px}}
				html.dark button.ga-launcher{background:#171717;border-color:#2c2c2c;box-shadow:0 8px 24px rgba(0,0,0,.4)}
				html.dark button.ga-launcher:hover{box-shadow:0 0 8px 0 #3c63be,0 0 18px 0 #76a00e,0 10px 28px rgba(0,0,0,.5)}
				html.dark .ga-label{color:#f7f6f3}
				.ga-iframe-wrap{position:fixed;right:24px;bottom:92px;z-index:2147483600;width:min(420px,calc(100vw - 32px));height:min(640px,calc(100vh - 132px));border-radius:16px;box-shadow:0 24px 48px rgba(0,0,0,.16);overflow:hidden;background:#f7f6f3;display:none;border:1px solid #ebebeb}
				.ga-iframe-wrap.open{display:block}
				.ga-iframe-wrap iframe{display:block;width:100%;height:100%;border:0;background:transparent}
				html.dark .ga-iframe-wrap{background:#09090a;border-color:#2c2c2c;box-shadow:0 24px 48px rgba(0,0,0,.5)}
			`;
    document.head.appendChild(styleEl);

    const launcher = document.createElement("button");
    launcher.className = "ga-launcher";
    launcher.setAttribute("aria-label", "Open Val");
    launcher.innerHTML =
      '<span class="ga-chip">' + MARK_SVG + '</span><span class="ga-label">Ask Val</span>';

    const wrap = document.createElement("div");
    wrap.className = "ga-iframe-wrap";

    let iframe = null;
    const ensureIframe = () => {
      if (iframe) return;
      iframe = document.createElement("iframe");
      iframe.src = iframeSrc();
      iframe.title = "Val";
      iframe.allow = "clipboard-write";
      // `allow-same-origin` so the React panel can use its own URL/storage.
      // `allow-forms` for the chat input's <form>. `allow-popups` +
      // `allow-popups-to-escape-sandbox` so the assistant's `docs:`-scheme
      // citation links and other `target="_blank"` links open in normal,
      // unsandboxed tabs.
      // Top-navigation remains disallowed so the iframe can't hijack the
      // docs host.
      iframe.setAttribute(
        "sandbox",
        "allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"
      );
      wrap.appendChild(iframe);
    };

    const toggle = () => {
      ensureIframe();
      wrap.classList.toggle("open");
    };

    launcher.addEventListener("click", toggle);

    // Escape closes the panel. We deliberately do NOT bind ⌘K/Ctrl+K on the
    // docs site: that chord belongs to Mintlify's built-in search, so the
    // launcher is click-to-open only here (the dashboard widget owns its own
    // ⌘K, where there's no search to collide with).
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && wrap.classList.contains("open")) {
        wrap.classList.remove("open");
      }
    });

    document.body.appendChild(launcher);
    document.body.appendChild(wrap);

    // Live theme sync: when the visitor toggles the Mintlify theme switcher,
    // forward the new mode to the iframe so the embedded panel re-themes
    // without needing a reload (matching the postMessage pattern used by the
    // product-onboarding embed for height updates).
    const themeObserver = new MutationObserver(() => {
      if (!iframe || !iframe.contentWindow) return;
      iframe.contentWindow.postMessage(
        { type: "galtea-theme", theme: currentDocsTheme() },
        "*"
      );
    });
    themeObserver.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount, { once: true });
  } else {
    mount();
  }
})();
