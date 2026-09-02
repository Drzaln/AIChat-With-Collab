/**
 * settings.js — controller for the unified Settings page.
 * Self-contained: this page does not load app.js, so it has its own
 * small `api()` helper (same contract as app.js's) and its own DOM
 * wiring. Relies on window.AIChatTheme from theme.js for the Appearance
 * tab's storage/validation/derivation logic.
 */
(function () {
    'use strict';

    // ── tiny api() helper, same contract as app.js's ──
    async function api(method, url, body = null) {
        const opts = { method, headers: { 'Content-Type': 'application/json' } };
        if (body) opts.body = JSON.stringify(body);

        let res;
        try {
            res = await fetch(url, opts);
        } catch (err) {
            return { error: `Network error: ${err.message}` };
        }

        let data;
        try {
            data = await res.json();
        } catch {
            data = { error: `Server returned an unexpected response (HTTP ${res.status})` };
        }

        if (!res.ok && !data.error) {
            data.error = `Request failed (HTTP ${res.status})`;
        }
        return data;
    }

    // ── Tab switching ──
    const TABS = ['configuration', 'appearance', 'notifications', 'data-backup'];

    function activateTab(tabName) {
        if (!TABS.includes(tabName)) tabName = TABS[0];

        document.querySelectorAll('.settings-nav-item').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        TABS.forEach(name => {
            const panel = document.getElementById(`tab-${name}`);
            if (panel) panel.hidden = name !== tabName;
        });

        try {
            const url = new URL(window.location.href);
            url.searchParams.set('tab', tabName);
            window.history.replaceState(null, '', url);
        } catch (err) { /* ignore (e.g. file:// URLs) */ }
    }

    document.querySelectorAll('.settings-nav-item').forEach(btn => {
        if (btn.disabled) return;
        btn.addEventListener('click', () => activateTab(btn.dataset.tab));
    });

    // Deep-link support: settings.html?tab=appearance
    const initialTab = new URLSearchParams(window.location.search).get('tab');
    activateTab(initialTab || 'configuration');

    // ══════════════════════════════════════════════════════
    //  Configuration tab
    // ══════════════════════════════════════════════════════
    async function loadConfigTab() {
        const config = await api('GET', '/api/config');
        document.getElementById('cfg-base-url').value = config.baseUrl || '';
        document.getElementById('cfg-api-key').value = config.apiKey || 'sk-colab-local';
        document.getElementById('cfg-model').value = config.modelName || 'character1';
    }

    function showConnectionResult(ok, message) {
        const el = document.getElementById('settings-connection-result');
        el.style.display = 'block';
        el.className = 'connection-result ' + (ok ? 'success' : 'error');
        el.textContent = message;
    }

    async function saveConfig() {
        const baseUrl = document.getElementById('cfg-base-url').value.trim();
        const apiKey = document.getElementById('cfg-api-key').value.trim();
        const modelName = document.getElementById('cfg-model').value;

        await api('POST', '/api/config', { baseUrl, apiKey, modelName });
        showConnectionResult(true, '✅ Settings saved.');
    }

    document.getElementById('btn-settings-save').addEventListener('click', saveConfig);

    document.getElementById('btn-settings-test-connection').addEventListener('click', async () => {
        const btn = document.getElementById('btn-settings-test-connection');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Testing...';

        try {
            // Save current field values first so the test uses the latest ones.
            const baseUrl = document.getElementById('cfg-base-url').value.trim();
            const apiKey = document.getElementById('cfg-api-key').value.trim();
            const modelName = document.getElementById('cfg-model').value;
            await api('POST', '/api/config', { baseUrl, apiKey, modelName });

            const result = await api('GET', '/api/test-connection');
            if (result.ok) {
                showConnectionResult(true, '✅ Connection successful! Server is healthy.');
            } else {
                showConnectionResult(false, `❌ ${result.error || 'Connection failed'}`);
            }
        } finally {
            btn.disabled = false;
            btn.innerHTML = '🔌 Test Connection';
        }
    });

    loadConfigTab();

    // ══════════════════════════════════════════════════════
    //  Appearance tab (theme)
    // ══════════════════════════════════════════════════════
    var accentPicker = document.getElementById('accent-picker');
    var bgPicker = document.getElementById('bg-picker');
    var accentValue = document.getElementById('accent-value');
    var bgValue = document.getElementById('bg-value');
    var saveIndicator = document.getElementById('save-indicator');
    var themeSaveTimer = null;

    function reflectThemeInputs(palette) {
        accentPicker.value = palette.accent;
        bgPicker.value = palette.background;
        accentValue.textContent = palette.accent.toUpperCase();
        bgValue.textContent = palette.background.toUpperCase();
    }

    function flashSaved() {
        saveIndicator.classList.add('show');
        clearTimeout(flashSaved._t);
        flashSaved._t = setTimeout(() => saveIndicator.classList.remove('show'), 1600);
    }

    function applyAndPersistTheme(palette) {
        window.AIChatTheme.set(palette);
        reflectThemeInputs(palette);
        clearTimeout(themeSaveTimer);
        themeSaveTimer = setTimeout(flashSaved, 120);
    }

    reflectThemeInputs(window.AIChatTheme.get());

    accentPicker.addEventListener('input', () => {
        applyAndPersistTheme({ accent: accentPicker.value, background: bgPicker.value });
    });
    bgPicker.addEventListener('input', () => {
        applyAndPersistTheme({ accent: accentPicker.value, background: bgPicker.value });
    });

    document.querySelectorAll('.preset-swatch').forEach(btn => {
        btn.addEventListener('click', () => {
            applyAndPersistTheme({ accent: btn.dataset.accent, background: btn.dataset.bg });
        });
    });

    document.getElementById('btn-apply-theme').addEventListener('click', () => {
        applyAndPersistTheme({ accent: accentPicker.value, background: bgPicker.value });
    });

    document.getElementById('btn-reset-theme').addEventListener('click', () => {
        window.AIChatTheme.reset();
        reflectThemeInputs(window.AIChatTheme.DEFAULTS);
        flashSaved();
    });
})();
