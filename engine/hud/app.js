'use strict';
let state=null, model='all', paused=false, lastMessage=0, selected=null;
const $=id=>document.getElementById(id);
const number=value=>value==null?'—':new Intl.NumberFormat('en-US').format(value);
const shortModel=name=>name?.includes('terra')?'Terra':name?.includes('luna')?'Luna':name?.includes('sol')?'Sol':name?.includes('astra')?'Astra':name||'Unknown';
const fits=name=>model==='all'||(name||'').includes(model);
function element(tag,text,cls){const e=document.createElement(tag);if(text!=null)e.textContent=text;if(cls)e.className=cls;return e;}
function time(value){return value?new Date(value*1000).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'}):'—';}
function saving(value,label){const box=element('div',null,'saving '+(value==null?'unknown':value>=0?'good':'bad'));box.append(element('small',label));box.append(element('strong',value==null?'—':`${value.toFixed(1)}%`));return box;}
function renderFocus(runs){if(!runs.some(r=>r.id===selected))selected=runs.find(r=>r.arm==='on')?.id||runs[0]?.id;const menu=$('focus-run');menu.replaceChildren(...runs.map(r=>{const option=element('option',`${shortModel(r.model)} · ${r.experiment} · ${r.arm==='on'?'Helix':'control'}`);option.value=r.id;option.selected=r.id===selected;return option;}));const current=runs.find(r=>r.id===selected);if(!current)return;const pair=state.pairs.find(p=>p.id===current.experiment_id),off=state.runs.find(r=>r.id===pair.off),on=state.runs.find(r=>r.id===pair.on);
 $('focus-title').textContent=`${shortModel(current.model)} ${current.effort||'effort unrecorded'} · ${current.experiment} · ${current.arm==='on'?'Helix candidate':'Control'}`;$('phase').textContent=`Observed phase: ${current.phase||'Unclassified'} · ${current.state} · ${current.usage_receipt_state==='LIVE_PREFIX_VALIDATED_UNSEALED'?'live counters, final receipt pending':current.usage_receipt_state==='SEALED'?'sealed counters':'counter binding unverified'} · receipt ${current.source_hash?.slice(0,12)||'unavailable'}`;
 const fields=[['Native input',r=>r?.usage?.input_tokens],['Native output',r=>r?.usage?.output_tokens],['Cached input (subset)',r=>r?.usage?.cached_input_tokens],['Uncached input',r=>r?.usage?.input_tokens!=null&&r?.usage?.cached_input_tokens!=null?r.usage.input_tokens-r.usage.cached_input_tokens:null],['Reported reasoning output',r=>r?.usage?.reasoning_output_tokens],['Raw source bytes',r=>r?.raw_source_bytes],['Model-visible bytes',r=>r?.model_visible_bytes],['Recorded tool bytes',r=>r?.recorded_tool_bytes],['Recorded commands',r=>r?.commands],['Observed pre-tool hooks',r=>r?.observed_pretool_hooks],['Command hooks without receipts',r=>r?.unmatched_pretool_hooks],['Engine calls',r=>r?.engine_calls],['Engine operations',r=>r?.engine_operations],['Suspected Engine-read output bytes',r=>r?.suspected_engine_read_output_bytes],['Generated command bytes',r=>r?.generated_command_bytes],['Glue / setup tokens',()=>null]];
 $('comparison').replaceChildren();for(const [label,get] of fields){const a=get(off),b=get(on),change=a!=null&&a>0&&b!=null?(b/a-1)*100:null;const tr=element('tr');tr.append(element('td',label),element('td',number(a)),element('td',number(b)),element('td',change==null?'—':`${change>0?'+':''}${change.toFixed(1)}%`,change==null?'muted':change<=0?'good':'bad'));$('comparison').append(tr);}const checked=r=>r?.artifact_check===true?'PASS':r?.artifact_check===false?'FAIL':'UNVERIFIED';const tr=element('tr');tr.append(element('td','Artifact checks'),element('td',checked(off)),element('td',checked(on)),element('td','Parity unproven','unknown'));$('comparison').append(tr);
 $('delegated').textContent=current.delegated_work;$('engine-time').textContent=current.engine_seconds==null?'Unmeasured':(current.engine_seconds*1000).toFixed(3)+' ms';$('mechanisms').textContent=Object.entries(current.mechanisms||{}).map(([k,v])=>`${k}: ${v}`).join(' · ');
 $('timeline').replaceChildren(...[...(current.timeline||[]),...(current.engine_timeline||[])].map(event=>{const li=element('li');const stamp=event.execution_timestamp==null?'—':String(event.execution_timestamp);li.append(element('span',stamp,'event-time'),element('span','#'+event.sequence,'event-seq'),element('span',event.type+' '+event.detail),element('span',event.recorded_output_bytes==null?'':number(event.recorded_output_bytes)+' B recorded','event-value'));if(event.exit_code!=null)li.append(element('span','exit '+event.exit_code,event.exit_code===0?'good':'bad'));return li;}));$('timeline-note').textContent='Native events then Engine events, each in source order · observed '+time(state.observed_at)+' · missing execution timestamps shown as —';
}
function render(){if(!state||paused)return;const runs=state.runs.filter(r=>fits(r.model)), pairs=state.pairs.filter(p=>fits(p.model));
 $('scope').textContent=state.scope;renderFocus(runs);renderCosts();renderEngineReplays();renderCohorts();
 $('active').textContent=runs.filter(r=>r.state==='RUNNING').length;
 $('active-note').textContent=`${runs.filter(r=>['STALE','RUNNING_UNVERIFIED'].includes(r.state)).length} stale / unverified process reports`;
 const totals=state.observed_totals?.[model==='all'?'all':Object.keys(state.observed_totals||{}).find(k=>k.includes(model))];
 for(const [id,key] of [['input','input_tokens'],['output','output_tokens']])$(id).textContent=number(totals?.usage?.[key]);
 $('total-scope').textContent=totals?`${totals.unique_threads} unique native threads · ${totals.aliases_removed} reused receipt aliases removed · ${totals.conflicting_threads} conflicting threads excluded · includes metered failed attempts`:'Verified thread totals unavailable';
 $('gaps').textContent=runs.filter(r=>r.usage?.input_tokens==null||r.usage?.output_tokens==null).length+' runs unmetered';
 $('scan-cost').textContent=state.observer?.last_scan_seconds!=null?(state.observer.last_scan_seconds*1000).toFixed(1)+' ms':'—';$('observer-reads').textContent=number(state.observer?.logical_file_bytes_read)+' B';
 $('count').textContent=pairs.length+' comparisons';$('scan').textContent=time(state.observer?.last_scan);$('revision').textContent='REV '+state.revision;
 $('updated').textContent='Snapshot '+time(state.observed_at);$('pairs').replaceChildren();
 for(const p of pairs){const card=element('article',null,'pair');const title=element('div');title.append(element('h3',p.name),element('div',shortModel(p.model)+' · '+p.classification,'meta'),element('div',p.artifact_check===true?'ARTIFACT CHECKS PASSED · PARITY UNPROVEN':p.artifact_check===false?'ARTIFACT CHECK FAILED':'ARTIFACT CHECKS UNVERIFIED','check'));card.append(title,saving(p.savings.input_tokens,'INPUT SAVED'),saving(p.savings.output_tokens,'OUTPUT SAVED'));$('pairs').append(card);}
 if(!pairs.length)$('pairs').append(element('p','No registered comparisons for this model.','empty'));
 $('runs').replaceChildren();for(const r of runs){const tr=element('tr');const values=[r.experiment+' / '+(r.arm==='off'?'control':'Helix'),shortModel(r.model),r.state,number(r.usage?.input_tokens),number(r.usage?.output_tokens),typeof r.elapsed_seconds==='number'?r.elapsed_seconds.toFixed(1)+'s':'—',r.last_event||'—'];values.forEach((v,i)=>tr.append(element('td',v,i===2?'state '+(['COMPLETED','CLOSED'].includes(r.state)?'good':r.state==='RUNNING'?'unknown':'bad'):null)));const td=element('td');const link=element('a','Receipt ↗');link.href='/api/receipt?id='+encodeURIComponent(r.id);link.target='_blank';link.rel='noopener';td.append(link);tr.append(td);$('runs').append(tr);}
 const alerts=[];if(state.observer?.error)alerts.push('Observer error: '+state.observer.error+'. Last snapshot may be stale.');for(const p of state.problems||[])if(runs.some(r=>r.id===p.run))alerts.push(p.message);for(const p of pairs)if(Object.values(p.savings).some(v=>v!=null&&v<0))alerts.push(shortModel(p.model)+' · '+p.name+' has a token regression.');if(runs.some(r=>r.state==='STALE'))alerts.push('A reported running process is no longer identifiable.');if(!alerts.length)alerts.push('No measured regression in this view. General parity remains unproven.');$('alerts').replaceChildren(...alerts.map(t=>element('li',t)));
}
for(const button of document.querySelectorAll('[data-model]'))button.addEventListener('click',()=>{model=button.dataset.model;for(const b of document.querySelectorAll('[data-model]')){b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button));}render();});
$('pause').addEventListener('click',()=>{paused=!paused;$('pause').textContent=paused?'Resume view':'Pause view';$('pause').setAttribute('aria-pressed',String(paused));if(!paused)render();updateConnection();});
function updateConnection(){const fresh=Date.now()-lastMessage<12000;const error=state?.observer?.error;const text=paused?'VIEW PAUSED':error?'OBSERVER ERROR':fresh?'LIVE · FILE OBSERVER':'DISCONNECTED';$('connection').textContent=text;$('light').style.background=fresh&&!error&&!paused?'var(--accent)':'var(--amber)';$('clock').textContent=new Date().toLocaleTimeString();}
const stream=new EventSource('/api/events');stream.onmessage=e=>{try{state=JSON.parse(e.data);lastMessage=Date.now();render();updateConnection();}catch(error){$('connection').textContent='INVALID TELEMETRY';}};stream.onerror=()=>{lastMessage=0;updateConnection();};setInterval(updateConnection,1000);
$('focus-run').addEventListener('change',()=>{selected=$('focus-run').value;if(!paused)render();});

function renderCosts(){
 const p=state.pricing||{};
 const fresh=p.fresh && Date.now()/1000<p.expires_at;
 $('price-status').textContent=(fresh?'CURRENT':'UNAVAILABLE / STALE')+' · checked '+(p.checked_at?new Date(p.checked_at*1000).toLocaleString():'never')+' · refresh every 2 min · expires after 5 min'+(p.error?' · latest refresh failed: '+p.error:'')+' · source hash '+(p.sha256?.slice(0,12)||'—');
 $('cost-rows').replaceChildren();
 const money=c=>c?'$'+c.short.toFixed(4)+' / $'+c.long.toFixed(4):'Unpriced';
 for(const pair of state.pairs.filter(p=>fits(p.model))){
  const a=fresh?state.costs?.[pair.off]:null,b=fresh?state.costs?.[pair.on]:null;
  const delta=a&&b?['short','long'].map(k=>a[k]>0?((1-b[k]/a[k])*100).toFixed(1)+'%':'—').join(' / '):'—';
  const tr=element('tr');
  tr.append(element('td',pair.name+' · '+shortModel(pair.model)),element('td',money(a)),element('td',money(b)),element('td',delta),element('td',pair.classification+' · '+(pair.artifact_check===true?'finite checks pass':'checks unverified/failed')));
  $('cost-rows').append(tr);
 }
 for(const name of ['Luna XHigh','Terra']){const tr=element('tr');tr.append(element('td',name),element('td','No matched receipts'),element('td','—'),element('td','—'),element('td','No substituted model or effort'));$('cost-rows').append(tr);}
}
function renderEngineReplays(){
 const body=$('engine-replays');body.replaceChildren();
 for(const row of state.engine_replays||[]){
  const tr=element('tr');
  const control=row.native_control;
  const native=control?shortModel(control.model)+' '+control.effort+' · '+control.usage.input_tokens.toLocaleString()+' / '+control.usage.output_tokens.toLocaleString():'No verified matched control';
  const saving=row.model_token_savings_percent;
  const avoided=saving?[saving.input_tokens,saving.output_tokens].map(v=>v==null?'—':v.toFixed(1)+'%').join(' / '):'—';
  for(const value of [row.case,row.state,row.model_calls??'Unknown',row.source_bytes??'—',row.answer_bytes??'—',row.elapsed_seconds!=null?(row.elapsed_seconds*1000).toFixed(2)+' ms':'—',native,avoided,row.scope])tr.append(element('td',String(value)));
  body.append(tr);
 }
 if(!body.children.length){const tr=element('tr'),td=element('td','No verified Engine execution registered.');td.colSpan=9;tr.append(td);body.append(tr);}
}
// Expire visible prices even if the observer connection has stopped delivering events.
setInterval(()=>{if(state){renderCosts();renderCohorts();}},1000);

function renderCohorts(){
 const body=$('cohorts');body.replaceChildren();
 const pct=n=>n==null?'—':n.toFixed(2)+'%';
 for(const c of (state.cohorts||[]).filter(c=>fits(c.model))){
  const tr=element('tr'),m=c.median_savings_percent,p=c.ratio_of_totals_savings_percent;
  const tariff=state.pricing?.fresh&&Date.now()/1000<state.pricing.expires_at?c.tariff_median_savings_percent:null;
  const values=[shortModel(c.model)+' '+c.effort,c.name,`${c.n_pairs}/${c.registered_pairs}`,pct(m.input_tokens),pct(m.output_tokens),pct(m.uncached_input_tokens),pct(tariff?.short)+' / '+pct(tariff?.long),pct(p.input_tokens)+' / '+pct(p.output_tokens),`${c.finite_check_passes} pass · ${c.finite_check_failures} fail · ${c.finite_check_unknown} unknown`,c.classification];
  values.forEach((v,i)=>tr.append(element('td',v,i>=3&&i<=5?([m.input_tokens,m.output_tokens,m.uncached_input_tokens][i-3]<0?'bad':''):null)));
  body.append(tr);
 }
 if(!body.children.length){const tr=element('tr'),td=element('td','No matched task cohort registered.');td.colSpan=10;tr.append(td);body.append(tr);}
}
