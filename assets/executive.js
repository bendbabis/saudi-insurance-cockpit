(function(){
"use strict";
var fields=[
["motor_rate_pct","Motor pricing", -40,60],["motor_cost_pct","Motor claims cost",-40,80],
["motor_volume_pct","Vehicle growth",-40,60],["health_rate_pct","Health repricing",-40,60],
["health_cost_pct","Medical inflation",-40,80],["health_volume_pct","Lives growth",-40,60],
["pc_growth_pct","P&C growth",-40,80],["pc_claims_pts","P&C claims ratio shift",-35,40],
["ps_growth_pct","P&S growth",-40,80],["expense_shift_pts","Expense ratio shift",-15,25],
["investment_change_pct","Investment result change",-100,100],["catastrophe_sar_m","Net catastrophe loss (SAR m)",0,10000],
["rbc_uplift_pct","Capital requirement stress",0,80],["capital_injection_sar_m","Capital injections (SAR m)",0,20000]
];
var presets={"Baseline":{},"Motor cost shock":{motor_cost_pct:12},"Medical inflation":{health_cost_pct:12,health_rate_pct:3},"Combined stress":{motor_cost_pct:12,health_cost_pct:10,catastrophe_sar_m:750,investment_change_pct:-25,rbc_uplift_pct:20},"Pricing recovery":{motor_rate_pct:10,health_rate_pct:9,motor_cost_pct:4,health_cost_pct:6}};
var values={},latest=null,configured=false;
function el(id){return document.getElementById(id)}
function txt(s){return String(s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
function n(x){return Number(x).toLocaleString("en-US",{maximumFractionDigits:2})}
async function request(path,options){var r=await fetch("/api"+path,Object.assign({headers:{"Content-Type":"application/json"}},options||{}));var d=await r.json();if(!r.ok)throw new Error(d.detail||"API error");return d}
function box(label,val,sub){return '<div class="card metric"><span>'+txt(label)+'</span><strong>'+txt(val)+'</strong><small>'+txt(sub)+'</small></div>'}
var btn=document.createElement("button");btn.id="siic-open";btn.textContent="✦ Executive Command Center";
var modal=document.createElement("div");modal.id="siic-modal";modal.setAttribute("role","dialog");modal.setAttribute("aria-label","Executive Command Center");
document.body.appendChild(btn);document.body.appendChild(modal);
var sliders=fields.map(function(f){return '<div class="slider"><label for="f-'+f[0]+'">'+f[1]+'</label><output id="v-'+f[0]+'">0</output><input id="f-'+f[0]+'" type="range" min="'+f[2]+'" max="'+f[3]+'" step="'+(f[3]>1000?50:1)+'" value="0"></div>'}).join("");
modal.innerHTML='<div class="inner"><div class="top"><div><p>SAUDI INSURANCE INTELLIGENCE · EXECUTIVE P0</p><h1>Insurance Industry Command Center</h1></div><div><span id="siic-status">Connecting…</span> <button id="siic-close">Return to classic cockpit ×</button></div></div>'+
'<div class="warn">OBSERVED: Q1 2026 metrics and FY2025 annual results are different reporting periods. MODELLED: What-if outputs are assumptions, not official IFRS 17 or capital calculations.</div>'+
'<section><div class="top"><h2>Latest official indicators · Q1 2026</h2><a href="https://www.ia.gov.sa/en/media-center/news/128" target="_blank" rel="noopener noreferrer">Insurance Authority · 8 September 2026</a></div><div id="siic-quarter" class="grid"></div></section>'+
'<section><h2>Annual reference · FY2025</h2><div id="siic-year" class="grid"></div><p>Historical cockpit transcription; metric-level independent reconciliation pending.</p></section>'+
'<section><div class="top"><h2>Actuarial Digital Twin · scenario engine</h2><div><select id="siic-preset">'+Object.keys(presets).map(function(x){return "<option>"+txt(x)+"</option>"}).join("")+'</select> <button id="siic-export">Export JSON</button></div></div>'+
'<div class="twocol"><div class="card"><h3>Scenario assumptions (percentage changes unless indicated)</h3><div class="slidergrid">'+sliders+'</div><p><button id="siic-run">Calculate scenario</button></p></div><div class="card"><h3>Financial & solvency impacts · MODELLED</h3><div id="siic-scenario">Run the model to view results.</div></div></div></section>'+
'<section><div class="twocol"><div class="card"><div class="top"><h2>Insurance Intelligence Copilot</h2><span id="siic-ai-state">Checking…</span></div><div id="siic-messages" class="messages"><div class="msg">Ask a market question. Responses use sourced structured market data; no company-level or full-document RAG yet.</div></div><form id="siic-chat" style="display:flex;gap:7px;margin-top:10px"><input id="siic-question" type="text" maxlength="3000" placeholder="Why did motor profitability deteriorate?" required><button id="siic-send">Ask AI</button></form><p>The provider key is configured only on the backend.</p></div>'+
'<div class="card"><h2>Official source monitor</h2><div id="siic-sources">Loading source registry…</div><p>Public URL discovery only. Unverified publications never overwrite dashboard data automatically.</p></div></div></section>'+
'<p>Methodology: docs/METHODOLOGY.md · Original eight-tab cockpit preserved · P0 is not a regulatory-grade production system.</p></div>';
btn.onclick=function(){modal.classList.add("visible");btn.style.display="none";load()};
el("siic-close").onclick=function(){modal.classList.remove("visible");btn.style.display=""};
modal.addEventListener("keydown",function(e){if(e.key==="Escape")el("siic-close").click()});
fields.forEach(function(f){el("f-"+f[0]).addEventListener("input",function(e){values[f[0]]=Number(e.target.value);el("v-"+f[0]).textContent=n(values[f[0]])})});
el("siic-preset").onchange=function(){var p=presets[this.value]||{};fields.forEach(function(f){values[f[0]]=p[f[0]]||0;el("f-"+f[0]).value=values[f[0]];el("v-"+f[0]).textContent=n(values[f[0]])});run()};
el("siic-run").onclick=run;
el("siic-export").onclick=function(){if(!latest)return;var u=URL.createObjectURL(new Blob([JSON.stringify(latest,null,2)],{type:"application/json"}));var a=document.createElement("a");a.href=u;a.download="siic-scenario.json";a.click();setTimeout(function(){URL.revokeObjectURL(u)},1000)};
async function load(){
try{
 var d=await request("/market/summary");el("siic-status").textContent="● Backend connected";
 el("siic-quarter").innerHTML=d.quarterly.metrics.map(function(m){return box(m.label,n(m.value)+(m.unit==="%"?"%":""),m.unit+" · official Q1 2026")}).join("");
 var a=d.annual;el("siic-year").innerHTML=[
 box("Gross written premium","SAR "+n(a.gwp_sar_m/1000)+"bn","FY2025"),
 box("Premium growth",n(a.gwp_growth_pct)+"%","Annual YoY"),
 box("Combined ratio",n(a.combined_ratio_pct)+"%","Annual"),
 box("Net income","SAR "+n(a.net_income_sar_m/1000)+"bn","Annual")].join("");
}catch(e){el("siic-status").textContent="Backend offline";el("siic-quarter").textContent="Start FastAPI to connect the executive view. Original cockpit remains accessible."}
try{var s=await request("/ai/status");configured=s.enabled;el("siic-ai-state").textContent=s.enabled?"AI ready · "+s.provider:s.note;el("siic-send").disabled=!s.enabled}catch(e){el("siic-ai-state").textContent="AI API unavailable";el("siic-send").disabled=true}
try{var c=await request("/market/sources");el("siic-sources").innerHTML=c.sources.map(function(s){return '<p><a href="'+txt(s.url)+'" target="_blank" rel="noopener noreferrer">'+txt(s.name)+'</a><br>Monitor: '+txt(s.status)+' · '+txt(s.last_checked||"not checked")+'</p>'}).join("")+'<p>'+c.discovered.length+' discovered unverified links shown.</p>'}catch(e){el("siic-sources").textContent="Source catalog unavailable"}
await run();
}
async function run(){
try{latest=await request("/scenarios/run",{method:"POST",body:JSON.stringify(values)});
var m=latest.market;
el("siic-scenario").innerHTML='<div class="grid" style="grid-template-columns:repeat(2,1fr)">'+[
 box("Scenario net combined ratio",n(m.scenario_combined_ratio_pct)+"%","Baseline "+n(m.baseline_combined_ratio_pct)+"%"),
 box("Scenario net income","SAR "+n(m.scenario_net_income_sar_m)+"m","FY2025 baseline + model deltas"),
 box("Underwriting delta","SAR "+n(m.underwriting_delta_sar_m)+"m","Vs model baseline"),
 box("Solvency proxy",n(m.scenario_solvency_proxy_pct)+"%","Simplified; not regulatory")].join("")+'</div>'+
 '<h3>Segment combined ratios</h3><table><tr><th>Segment</th><th>Base</th><th>Scenario</th></tr>'+
 latest.segments.map(function(s){return '<tr><td>'+txt(s.segment)+'</td><td>'+n(s.baseline_combined_ratio_pct)+'%</td><td>'+n(s.scenario_combined_ratio_pct)+'%</td></tr>'}).join("")+'</table><div class="warn">'+txt(latest.warnings[0])+' '+txt(latest.warnings[1])+'</div>';
}catch(e){el("siic-scenario").textContent="Scenario unavailable: "+e.message}
}
el("siic-chat").onsubmit=async function(e){e.preventDefault();var q=el("siic-question").value.trim();if(!q)return;var log=el("siic-messages");var user=document.createElement("div");user.className="msg user";user.textContent=q;log.append(user);el("siic-question").value="";
var response=document.createElement("div");response.className="msg";response.textContent="Analyzing structured evidence…";log.append(response);log.scrollTop=log.scrollHeight;el("siic-send").disabled=true;
try{var a=await request("/ai/chat",{method:"POST",body:JSON.stringify({message:q})});response.textContent=a.answer+"\nEvidence: "+a.evidence.join(" · ")+"\n"+a.limitations}catch(err){response.textContent="AI error: "+err.message}finally{el("siic-send").disabled=!configured;log.scrollTop=log.scrollHeight}};
})();