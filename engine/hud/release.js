'use strict';
let snapshot = null, filter = 'all', paused = false, seen = 0, lastRender = '';
const $ = id => document.getElementById(id);
const el = (tag, text, cls) => { const n = document.createElement(tag); if(text != null) n.textContent = text; if(cls) n.className = cls; return n; };
const fmt = n => n == null ? '—' : new Intl.NumberFormat('en-US', {maximumFractionDigits:1}).format(n);
const pct = n => n == null ? '—' : n.toFixed(1) + '%';
const name = lane => (lane.model.includes('luna') ? 'Luna' : lane.model.includes('sol') ? 'Sol' : 'Astra') + ' ' + (lane.effort === 'xhigh' ? 'XHigh' : 'High');
const lanes = () => (snapshot?.release?.lanes || []).filter(l => filter === 'all' || l.model.includes(filter));
const safeLink = (text, url) => { const a = el('a', text); if(url?.startsWith('https://github.com/SuperHelix77/HelixContext/')) {a.href = url; a.target = '_blank'; a.rel = 'noopener';} return a; };
function card(lane) {
  const n = el('article', null, 'model-card'), title = el('div', null, 'card-title');
  title.append(el('h3', name(lane)), el('span', lane.state.startsWith('REJECTED') ? 'Rejected · N = 1' : lane.arms.length ? 'N = 1 · development' : 'Pending', 'badge'));
  n.append(title, el('p', lane.task, 'task'), el('p', lane.policy, 'policy'));
  const values = el('div', null, 'card-values');
  for(const [key, label] of [['input_tokens','INPUT SAVED'], ['output_tokens','OUTPUT SAVED']]) {
    const v = lane.savings?.[key], cell = el('div');
    cell.append(el('strong', pct(v), v == null ? '' : v < 0 ? 'negative' : 'positive'), el('small', label)); values.append(cell);
  }
  n.append(values, el('p', lane.gate, 'gate'), el('p', 'Model-wide parity: unconfirmed · full-cohort median: unavailable', 'small'));
  const details = el('details'); details.append(el('summary', 'Scope, caveats & exact final answers'));
  const ul = el('ul'); for(const t of lane.limits || []) ul.append(el('li', t)); details.append(ul);
  for(const a of lane.arms) details.append(safeLink(a.arm === 'off' ? 'Control final ↗ ' : 'Helix final ↗ ', a.final_url));
  n.append(details);
  const links = el('div', null, 'receipt-links');
  if(lane.report_url) links.append(safeLink('Paired receipt ↗', lane.report_url), safeLink('Semantic review ↗', lane.review_url));
  n.append(links, el('p', 'CAPSULE ' + lane.capsule_sha256.slice(0,16), 'hash'));
  return n;
}
function pricesFresh() { const p = snapshot?.pricing; return p?.fresh && Date.now()/1000 < p.expires_at; }
function costView() {
  if(!snapshot) return;
  const fresh = pricesFresh(), p = snapshot.pricing || {}, tier = $('tariff').value;
  $('price-status').textContent = (fresh ? 'CURRENT' : 'UNAVAILABLE / STALE — costs withheld') + ' · official Standard prices · checked ' + (p.checked_at ? new Date(p.checked_at*1000).toLocaleString() : 'never') + ' · refresh 2 min / expire 5 min' + (p.error ? ' · refresh failed' : '');
  $('cost-table').replaceChildren(); $('frontier-plot').replaceChildren();
  for(const l of lanes()) {
    const a = fresh ? l.costs?.off?.[tier] : null, b = fresh ? l.costs?.on?.[tier] : null;
    const saved = a > 0 && b != null ? 100*(1-b/a) : null;
    const row = el('tr');
    for(const value of [name(l)+' / '+l.task, pct(l.savings?.input_tokens), pct(l.savings?.output_tokens), pct(l.savings?.uncached_input_tokens), a == null ? 'Unpriced' : '$'+a.toFixed(4), b == null ? 'Unpriced' : '$'+b.toFixed(4), pct(saved)]) row.append(el('td', value));
    $('cost-table').append(row);
    if(a > 0 && b != null) {
      const ratio = b/a, track = el('div', null, 'track'), bar = el('div', null, 'bar'+(ratio > 1 ? ' negative' : ''));
      bar.style.width = Math.min(ratio*100, 100)+'%'; track.append(bar);
      const r = el('div', null, 'frontier-row');
      const gate = l.comparison_gate || 'PASS';
      r.title = l.task + ' · bounded task/final gate '+gate+'; one development pair. Own control = 100%. ' + (ratio > 1 ? 'Bar capped at100%; exact ratio shown.' : '');
      r.append(el('span',name(l)+' · '+gate), track, el('span',(ratio*100).toFixed(1)+'%', 'ratio')); $('frontier-plot').append(r);
    }
  }
  if(!$('frontier-plot').children.length) $('frontier-plot').append(el('p','No currently priced, paired evidence in this view.', 'empty'));
}
function liveView() {
  const all = snapshot?.runs || [], active = all.filter(r => r.state === 'RUNNING');
  $('active-runs').textContent = active.length;
  const o = snapshot?.observer || {};
  $('scan-ms').textContent = o.last_scan_seconds == null ? '—' : fmt(o.last_scan_seconds*1000)+' ms';
  $('scan-at').textContent = o.last_scan ? new Date(o.last_scan*1000).toLocaleTimeString() : 'No scan';
  $('io-bytes').textContent = o.logical_file_bytes_read == null ? '—' : o.logical_file_bytes_read < 1e6 ? fmt(o.logical_file_bytes_read/1000)+' KB' : fmt(o.logical_file_bytes_read/1e6)+' MB';
  const events = active.flatMap(r => [...(r.timeline || []),...(r.engine_timeline || [])].slice(-8).map(e => ({...e,run:r.model+' / '+r.arm})));
  $('events').replaceChildren();
  for(const e of events.slice(-16)) { const li = el('li'); li.append(el('time',e.execution_timestamp == null ? 'time unavailable' : String(e.execution_timestamp)), el('span',e.run+' · '+e.type+' · '+e.detail)); $('events').append(li); }
  if(!events.length) $('events').append(el('li','No active native execution events. Sealed results remain in the research ledger.'));
  const m = $('mechanisms'); m.replaceChildren();
  const mechanismText = active.map(r => Object.entries(r.mechanisms || {}).map(([k,v]) => k+': '+v).join(', ')).filter(Boolean).join(' / ');
  const peers = (snapshot?.peer_states || []).map(p => p.name+': '+p.state).join(' / ');
  for(const [k,v] of [['Active-run mechanisms', mechanismText || 'No active source'],['Hot / cold evidence sizes','Unmeasured'],['Plan reuse / break-even','No live source registered'],['Observed peer-state files',peers || 'No live source registered'],['Compaction restoration ACK','Unverified']]) {const d=el('div');d.append(el('dt',k),el('dd',v));m.append(d);}
  const alerts = [];
  for(const p of snapshot?.release?.problems || []) alerts.push('Evidence withdrawn: '+p.error);
  if(o.error) alerts.push('Observer error: '+o.error+'; last snapshot may be stale.');
  for(const l of lanes()) if(Object.values(l.savings || {}).some(v => v != null && v < 0)) alerts.push(name(l)+' / '+l.task+': token regression retained.');
  if(!pricesFresh()) alerts.push('Official tariffs unavailable or expired. Price comparisons are withheld.');
  alerts.push('Full-model parity and seven-cell release medians are not confirmed.');
  $('alerts').replaceChildren(...alerts.map(t => el('li',t)));
}
function render() {
  if(!snapshot || paused) return;
  const signature = JSON.stringify([filter,snapshot.release]);
  if(signature !== lastRender) {$('model-cards').replaceChildren(...lanes().map(card)); lastRender=signature;}
  $('version').textContent = snapshot.release?.version || 'Evidence unavailable';
  $('updated').textContent = 'Observed '+(snapshot.observed_at ? new Date(snapshot.observed_at*1000).toLocaleString() : '—');
  costView(); liveView();
}
function connection() {
  const fresh = Date.now()-seen < 12000;
  $('connection').textContent = paused ? 'VIEW PAUSED' : !fresh ? 'DISCONNECTED' : snapshot?.observer?.error ? 'OBSERVER ERROR' : 'LIVE · READ ONLY';
}
function accept(s) {snapshot=s;seen=Date.now();render();connection();}
const stream = new EventSource('/api/release-events');
stream.onmessage = e => {try {accept(JSON.parse(e.data));} catch {seen=0;$('connection').textContent='INVALID TELEMETRY';}};
stream.onerror = () => {seen=0;connection();};
fetch('/api/release-state').then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json();}).then(accept).catch(()=>{if(!snapshot)$('connection').textContent='CONNECTING / RETRYING';});
for(const b of document.querySelectorAll('[data-model]')) b.addEventListener('click',()=>{filter=b.dataset.model;for(const x of document.querySelectorAll('[data-model]'))x.setAttribute('aria-pressed',String(x===b));render();});
$('tariff').addEventListener('change',costView);
$('pause').addEventListener('click',()=>{paused=!paused;$('pause').textContent=paused?'Resume view':'Pause view';$('pause').setAttribute('aria-pressed',String(paused));if(!paused)render();connection();});
$('export').addEventListener('click',()=>{
  if(!snapshot)return;
  const data={schema:'helix.release-public-export.v1',observed_at:snapshot.observed_at,release:structuredClone(snapshot.release),
    pricing:{...snapshot.pricing,rates:pricesFresh()?snapshot.pricing?.rates:null,fresh:pricesFresh()},
    cost_scope:'Public paired-token evidence. Full effective cost and included quota unknown.'};
  if(!pricesFresh())for(const l of data.release?.lanes || [])l.costs={};
  const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)+'\n'],{type:'application/json'})),a=el('a');
  a.href=url;a.download='helix-evidence-snapshot.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
setInterval(()=>{connection();if(snapshot){costView();if(!paused)liveView();}},1000);
