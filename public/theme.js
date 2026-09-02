/**
 * theme.js — shared theme engine (C7)
 *
 * Loaded as a plain, blocking <script> (not `defer`/`module`) right after
 * styles.css on every page, so the saved palette is applied to :root
 * before the page paints — no flash of the default purple theme.
 *
 * Only two CSS variables are ever set here: --accent-base and --bg-base.
 * Every other themed color in styles.css is derived from those two via
 * color-mix(), so this file stays tiny and can't drift out of sync with
 * the rest of the palette.
 */
(function () {
    'use strict';

    var STORAGE_KEY = 'aichat-theme-palette';
    var DEFAULTS = { accent: '#A855F7', background: '#121212' };

    function hexToRgb(hex) {
        var clean = (hex || '').replace('#', '');
        if (clean.length === 3) {
            clean = clean.split('').map(function (c) { return c + c; }).join('');
        }
        var n = parseInt(clean, 16);
        if (isNaN(n) || clean.length !== 6) return { r: 0, g: 0, b: 0 };
        return { r: (n >> 16) & 255, g: (n >> 8) & 255, b: n & 255 };
    }

    // WCAG relative luminance — used to decide whether text on top of the
    // user's chosen background should be light or dark.
    function relativeLuminance(hex) {
        var rgb = hexToRgb(hex);
        var chans = [rgb.r, rgb.g, rgb.b].map(function (v) {
            var c = v / 255;
            return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * chans[0] + 0.7152 * chans[1] + 0.0722 * chans[2];
    }

    function loadPalette() {
        try {
            var raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return null;
            var parsed = JSON.parse(raw);
            if (parsed && /^#[0-9a-fA-F]{6}$/.test(parsed.accent) && /^#[0-9a-fA-F]{6}$/.test(parsed.background)) {
                return parsed;
            }
            return null;
        } catch (err) {
            console.warn('[theme] could not read saved palette:', err);
            return null;
        }
    }

    function applyPalette(palette) {
        var root = document.documentElement;
        root.style.setProperty('--accent-base', palette.accent);
        root.style.setProperty('--bg-base', palette.background);
        root.style.setProperty('--text-primary', relativeLuminance(palette.background) > 0.5 ? '#16151A' : '#E8E6E3');
        root.style.setProperty('--text-on-accent', relativeLuminance(palette.accent) > 0.5 ? '#16151A' : '#FFFFFF');
    }

    function savePalette(palette) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(palette));
            return true;
        } catch (err) {
            console.warn('[theme] could not persist palette:', err);
            return false;
        }
    }

    // Applied immediately on script evaluation (this script is loaded
    // synchronously in <head>, so this runs before body content paints).
    var current = loadPalette() || DEFAULTS;
    applyPalette(current);

    // Exposed for the theme settings page (and anything else that wants
    // to read/change the palette at runtime) without re-implementing the
    // storage/validation/derivation logic.
    window.AIChatTheme = {
        DEFAULTS: DEFAULTS,
        get: function () { return loadPalette() || DEFAULTS; },
        set: function (palette) {
            applyPalette(palette);
            return savePalette(palette);
        },
        reset: function () {
            try { localStorage.removeItem(STORAGE_KEY); } catch (err) { /* ignore */ }
            applyPalette(DEFAULTS);
        }
    };
})();
