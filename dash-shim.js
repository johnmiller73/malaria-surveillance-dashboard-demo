// Minimal stand-in for the dashboard runtime the page was written for.
// Provides dash.data, dash.draw, dash.onData, dash.params/setParams/resetParams, dash.colors.
// Data comes from window.SAMPLE_CSV (data/data.js) or, failing that, the CSV files in data/.
(function () {
  const DEFAULTS = {state: '', lga: '', metric: 'cases', scope: 'children', sys: 'all', rank: 'gap', topn: '15'};
  const SOURCES = {geo: 'data/geo_2025.csv', trend: 'data/trend_2021_2025.csv'};
  const store = {};
  const draws = [];
  const listeners = [];
  let params = Object.assign({}, DEFAULTS, readHash());
  let pending = false;

  function readHash() {
    const out = {};
    new URLSearchParams(location.hash.replace(/^#/, '')).forEach((v, k) => { if (k in DEFAULTS) out[k] = v; });
    return out;
  }
  function writeHash() {
    const q = new URLSearchParams();
    for (const k of Object.keys(DEFAULTS)) if (params[k] !== DEFAULTS[k] && params[k] !== '') q.set(k, params[k]);
    const h = q.toString();
    history.replaceState(null, '', h ? '#' + h : location.pathname + location.search);
  }
  function schedule() {
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => { pending = false; render(); });
  }
  function render() {
    for (const fn of listeners) { try { fn(); } catch (e) { console.error(e); } }
    for (const [name, fn] of draws) {
      document.querySelectorAll('[data-draw="' + name + '"]').forEach((el) => {
        if (el.closest('[hidden]')) return;
        try { fn(el); } catch (e) { console.error('draw ' + name, e); }
      });
    }
  }
  function setRows(id, text) {
    const rows = d3.csvParse(text, (r) => { for (const k in r) if (r[k] === '') r[k] = null; return r; });
    store[id] = {status: 'ok', data: rows, columns: rows.columns, message: null, refreshing: false};
  }

  const cssVar = (n) => 'var(' + n + ')';
  window.dash = {
    colors: [cssVar('--series-0'), cssVar('--series-1'), cssVar('--series-2'), cssVar('--series-3')],
    data(id) { return store[id] || {status: 'loading', data: [], message: null, refreshing: false}; },
    onData(fn) { listeners.push(fn); try { fn(); } catch (e) { console.error(e); } },
    draw(name, fn) {
      if (typeof fn === 'function') draws.push([name, fn]);
      else if (fn && typeof fn.update === 'function') draws.push([name, fn.update]);
      else document.querySelectorAll('[data-draw="' + name + '"]').length && schedule();
    },
    params() { return Object.assign({}, params); },
    setParams(o) { for (const k in o) params[k] = o[k] == null ? DEFAULTS[k] ?? '' : String(o[k]); writeHash(); schedule(); },
    resetParams() { params = Object.assign({}, DEFAULTS); writeHash(); schedule(); },
    setLink() {},
    refresh() {},
    calc() {},
    loader() {},
    async start() {
      const embedded = window.SAMPLE_CSV || {};
      await Promise.all(Object.entries(SOURCES).map(async ([id, url]) => {
        try {
          if (embedded[id]) setRows(id, embedded[id]);
          else setRows(id, await (await fetch(url)).text());
        } catch (e) {
          console.error('Could not load ' + url, e);
          store[id] = {status: 'error', data: [], message: String(e)};
        }
      }));
      render();
      let w = window.innerWidth;
      window.addEventListener('resize', () => { if (window.innerWidth !== w) { w = window.innerWidth; schedule(); } });
      window.addEventListener('hashchange', () => { params = Object.assign({}, DEFAULTS, readHash()); schedule(); });
    }
  };
})();
