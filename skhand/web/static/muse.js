/* Writer's Muse — Shared JS utilities */

const Muse = {
    /**
     * POST JSON to an API endpoint and return parsed response.
     */
    async post(url, data) {
        const resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ error: resp.statusText }));
            throw new Error(err.error || 'Request failed');
        }
        return resp.json();
    },

    /**
     * GET JSON from an API endpoint.
     */
    async get(url) {
        const resp = await fetch(url);
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ error: resp.statusText }));
            throw new Error(err.error || 'Request failed');
        }
        return resp.json();
    },

    /**
     * Map tradition name to a CSS tag class.
     */
    traditionTag(tradition) {
        const t = (tradition || '').toLowerCase();
        if (t.includes('vedic') || t.includes('hindu') || t.includes('indian')) return 'tag-vedic';
        if (t.includes('greek')) return 'tag-greek';
        if (t.includes('norse') || t.includes('germanic')) return 'tag-norse';
        if (t.includes('egypt')) return 'tag-egyptian';
        if (t.includes('chinese')) return 'tag-chinese';
        if (t.includes('african') || t.includes('mande') || t.includes('yoruba')) return 'tag-african';
        if (t.includes('mesopotam') || t.includes('babylon') || t.includes('sumer')) return 'tag-mesopotamian';
        if (t.includes('celtic') || t.includes('irish')) return 'tag-celtic';
        if (t.includes('buddhis')) return 'tag-buddhist';
        return 'tag-vedic'; // default
    },

    /**
     * Truncate text to maxLen characters with ellipsis.
     */
    truncate(text, maxLen = 200) {
        if (!text || text.length <= maxLen) return text || '';
        return text.substring(0, maxLen) + '...';
    },

    /**
     * Render markdown using marked.js (if available).
     */
    renderMarkdown(text) {
        if (typeof marked !== 'undefined') {
            return marked.parse(text || '');
        }
        return (text || '').replace(/\n/g, '<br>');
    },

    /**
     * Copy text to clipboard.
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch {
            return false;
        }
    },

    /**
     * Download text as a file.
     */
    downloadFile(content, filename, mimeType = 'text/markdown') {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    },

    /**
     * Get selected checkbox values from a group.
     */
    getCheckedValues(name) {
        return Array.from(document.querySelectorAll(`input[name="${name}"]:checked`))
            .map(cb => cb.value);
    },

    /**
     * Save generation to localStorage history.
     */
    saveToHistory(type, data) {
        const history = JSON.parse(localStorage.getItem('muse_history') || '[]');
        history.unshift({
            type,
            data,
            timestamp: new Date().toISOString(),
        });
        // Keep last 50
        localStorage.setItem('muse_history', JSON.stringify(history.slice(0, 50)));
    },

    /**
     * Get generation history from localStorage.
     */
    getHistory() {
        return JSON.parse(localStorage.getItem('muse_history') || '[]');
    },
};
