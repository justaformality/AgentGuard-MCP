import { useCallback, useEffect, useMemo, useState } from "react";
import "./index.css";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

type Agent = { id:number; name:string; role:string; status:string; allowed_tools:string[]; blocked_tools:string[]; approval_rules:Record<string,unknown>; created_at:string; updated_at:string };
type Tool = { id:number; name:string; description:string; category:string; risk_level:string; action_type:string; requires_approval:boolean; enabled:boolean; created_at:string; updated_at:string };
type Approval = { id:number; agent_id:number; tool_id:number; input_summary:string; proposed_action:Record<string,unknown>; status:string; decision_reason?:string|null; created_at:string; decided_at?:string|null };
type Audit = { id:number; agent_id?:number|null; tool_id?:number|null; agent_name?:string|null; tool_name?:string|null; input_summary:string; output_summary?:string|null; status:string; risk_level?:string|null; approval_status?:string|null; error_message?:string|null; created_at:string };
type Tab = "Overview"|"Agents"|"Tools"|"Approvals"|"Audit"|"Runner";

async function api<T>(path:string, init?:RequestInit):Promise<T>{
  const res = await fetch(`${API}${path}`, { headers:{"Content-Type":"application/json", ...(init?.headers||{})}, ...init });
  if(!res.ok){ const body = await res.text(); throw new Error(body || `${res.status} ${res.statusText}`); }
  return res.json();
}

const pill = (value:string) => {
  const v=value.toLowerCase();
  if(["high","blocked","failed","rejected"].includes(v)) return "bg-red-500/10 text-red-300 border-red-500/20";
  if(["medium","pending","pending_approval"].includes(v)) return "bg-amber-500/10 text-amber-300 border-amber-500/20";
  if(["low","completed","allowed","active","approved"].includes(v)) return "bg-emerald-500/10 text-emerald-300 border-emerald-500/20";
  return "bg-slate-500/10 text-slate-300 border-slate-500/20";
};

function App(){
  const [tab,setTab]=useState<Tab>("Overview");
  const [agents,setAgents]=useState<Agent[]>([]); const [tools,setTools]=useState<Tool[]>([]); const [approvals,setApprovals]=useState<Approval[]>([]); const [audit,setAudit]=useState<Audit[]>([]);
  const [loading,setLoading]=useState(true); const [error,setError]=useState(""); const [notice,setNotice]=useState("");
  const [runnerAgent,setRunnerAgent]=useState<number|"">(""); const [runnerTool,setRunnerTool]=useState<number|"">(""); const [runnerInput,setRunnerInput]=useState("Generate a regression test plan for password reset."); const [runnerResult,setRunnerResult]=useState<unknown>(null);

  const load=useCallback(async()=>{
    setError("");
    try{
      const [a,t,p,l]=await Promise.all([api<Agent[]>("/agents"),api<Tool[]>("/tools"),api<Approval[]>("/approvals"),api<Audit[]>("/audit-logs")]);
      setAgents(a);setTools(t);setApprovals(p);setAudit(l); if(runnerAgent===""&&a[0])setRunnerAgent(a[0].id); if(runnerTool===""&&t[0])setRunnerTool(t[0].id);
    }catch(e){setError(e instanceof Error?e.message:String(e));}finally{setLoading(false);}
  },[runnerAgent,runnerTool]);
  useEffect(()=>{void load()},[]); // eslint-disable-line react-hooks/exhaustive-deps

  const pending=approvals.filter(a=>a.status==="pending");
  const stats=[
    ["Registered agents",agents.length,"Active identities governed"],
    ["Enabled tools",tools.filter(t=>t.enabled).length,`${tools.filter(t=>t.requires_approval).length} approval-gated`],
    ["Pending approvals",pending.length,"Human decisions required"],
    ["Audit events",audit.length,"Every governed call recorded"],
  ];
  const agentById=useMemo(()=>Object.fromEntries(agents.map(a=>[a.id,a])),[agents]); const toolById=useMemo(()=>Object.fromEntries(tools.map(t=>[t.id,t])),[tools]);

  async function saveAgent(agent:Agent, allowed:string[]){
    try{ await api(`/agents/${agent.id}`,{method:"PUT",body:JSON.stringify({allowed_tools:allowed,blocked_tools:agent.blocked_tools.filter(x=>!allowed.includes(x))})}); setNotice(`Saved permissions for ${agent.name}.`); await load(); }catch(e){setError(String(e));}
  }
  async function toggleTool(tool:Tool){ try{await api(`/tools/${tool.id}`,{method:"PUT",body:JSON.stringify({enabled:!tool.enabled})});await load();}catch(e){setError(String(e));} }
  async function decide(id:number,action:"approve"|"reject"){ try{const reason=action==="approve"?"Approved from AgentGuard dashboard.":"Rejected from AgentGuard dashboard.";await api(`/approvals/${id}/${action}`,{method:"POST",body:JSON.stringify({decision_reason:reason})});setNotice(`Approval ${id} ${action}d.`);await load();}catch(e){setError(String(e));} }
  async function runTask(){ if(runnerAgent===""||runnerTool==="")return; setRunnerResult(null); try{const r=await api("/run-agent-task",{method:"POST",body:JSON.stringify({agent_id:runnerAgent,tool_id:runnerTool,input_text:runnerInput})});setRunnerResult(r);await load();}catch(e){setRunnerResult({error:String(e)});} }

  return <div className="min-h-screen bg-[#070b14] text-slate-100">
    <div className="flex min-h-screen">
      <aside className="hidden w-64 shrink-0 border-r border-white/10 bg-[#0a1020] p-5 lg:block">
        <div className="mb-8"><div className="text-xs font-semibold uppercase tracking-[.28em] text-cyan-300">AgentGuard</div><div className="mt-1 text-xl font-bold">MCP Governance</div></div>
        <nav className="space-y-1">{(["Overview","Agents","Tools","Approvals","Audit","Runner"] as Tab[]).map(x=><button key={x} onClick={()=>setTab(x)} className={`w-full rounded-xl px-4 py-3 text-left text-sm ${tab===x?"bg-cyan-400/10 text-cyan-200":"text-slate-400 hover:bg-white/5 hover:text-white"}`}>{x}{x==="Approvals"&&pending.length>0?<span className="float-right rounded-full bg-amber-400/15 px-2 text-amber-300">{pending.length}</span>:null}</button>)}</nav>
        <div className="mt-10 rounded-xl border border-white/10 bg-white/5 p-4 text-xs text-slate-400"><div className="mb-1 font-semibold text-slate-200">Governance model</div>Read calls may run automatically. High-risk write/execute actions stop at a human approval gate.</div>
      </aside>
      <main className="min-w-0 flex-1 p-4 md:p-8">
        <div className="mx-auto max-w-7xl">
          <header className="mb-7 flex flex-wrap items-center justify-between gap-4"><div><p className="text-sm text-cyan-300">AI agent control plane</p><h1 className="text-3xl font-bold">{tab}</h1></div><div className="flex items-center gap-3"><span className={`rounded-full border px-3 py-1 text-xs ${error?pill("failed"):pill("active")}`}>{error?"Backend unavailable":"Backend connected"}</span><button onClick={()=>void load()} className="rounded-xl border border-white/10 px-4 py-2 text-sm hover:bg-white/5">Refresh</button></div></header>
          <div className="mb-5 flex gap-2 overflow-x-auto lg:hidden">{(["Overview","Agents","Tools","Approvals","Audit","Runner"] as Tab[]).map(x=><button key={x} onClick={()=>setTab(x)} className={`whitespace-nowrap rounded-lg px-3 py-2 text-sm ${tab===x?"bg-cyan-400/10 text-cyan-200":"bg-white/5 text-slate-400"}`}>{x}</button>)}</div>
          {notice&&<div className="mb-5 rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">{notice}</div>}
          {error&&<div className="mb-5 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</div>}
          {loading?<div className="py-20 text-center text-slate-400">Loading governance data…</div>:<>
            {tab==="Overview"&&<><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{stats.map(([a,b,c])=><div key={a as string} className="card"><p className="text-sm text-slate-400">{a}</p><div className="mt-2 text-3xl font-bold">{b}</div><p className="mt-2 text-xs text-slate-500">{c}</p></div>)}</div><div className="mt-6 grid gap-6 xl:grid-cols-2"><section className="card"><h2 className="section-title">Recent tool calls</h2><div className="space-y-3">{audit.slice(0,6).map(x=><div key={x.id} className="row"><div><div className="font-medium">{x.tool_name||"Unknown tool"}</div><div className="text-xs text-slate-500">{x.agent_name||"Unknown agent"} · {new Date(x.created_at).toLocaleString()}</div></div><span className={`pill ${pill(x.status)}`}>{x.status}</span></div>)}{audit.length===0&&<Empty text="No tool calls yet."/>}</div></section><section className="card"><h2 className="section-title">Approval queue</h2><div className="space-y-3">{pending.slice(0,6).map(x=><div key={x.id} className="row"><div><div className="font-medium">{toolById[x.tool_id]?.name||`Tool ${x.tool_id}`}</div><div className="text-xs text-slate-500">{agentById[x.agent_id]?.name||`Agent ${x.agent_id}`}</div></div><span className={`pill ${pill("pending")}`}>pending</span></div>)}{pending.length===0&&<Empty text="No pending approvals."/>}</div></section></div></>}
            {tab==="Agents"&&<div className="grid gap-5 xl:grid-cols-2">{agents.map(agent=><AgentCard key={agent.id} agent={agent} tools={tools} onSave={saveAgent}/>)}</div>}
            {tab==="Tools"&&<div className="card overflow-x-auto"><table className="w-full min-w-[800px] text-left text-sm"><thead className="text-xs uppercase text-slate-500"><tr><th className="pb-3">Tool</th><th>Category</th><th>Risk</th><th>Action</th><th>Approval</th><th>Enabled</th></tr></thead><tbody>{tools.map(t=><tr key={t.id} className="border-t border-white/5"><td className="py-4 pr-5"><div className="font-medium">{t.name}</div><div className="mt-1 max-w-xl text-xs text-slate-500">{t.description}</div></td><td>{t.category}</td><td><span className={`pill ${pill(t.risk_level)}`}>{t.risk_level}</span></td><td>{t.action_type}</td><td>{t.requires_approval?"Required":"Automatic"}</td><td><button onClick={()=>void toggleTool(t)} className={`rounded-lg border px-3 py-1 text-xs ${t.enabled?pill("active"):pill("blocked")}`}>{t.enabled?"Enabled":"Disabled"}</button></td></tr>)}</tbody></table></div>}
            {tab==="Approvals"&&<div className="space-y-4">{approvals.map(a=><section key={a.id} className="card"><div className="flex flex-wrap items-start justify-between gap-3"><div><div className="font-semibold">{toolById[a.tool_id]?.name||`Tool ${a.tool_id}`}</div><div className="mt-1 text-sm text-slate-400">Requested by {agentById[a.agent_id]?.name||`Agent ${a.agent_id}`} · {new Date(a.created_at).toLocaleString()}</div></div><span className={`pill ${pill(a.status)}`}>{a.status}</span></div><pre className="mt-4 max-h-52 overflow-auto whitespace-pre-wrap rounded-xl bg-black/25 p-4 text-xs text-slate-300">{a.input_summary}</pre>{a.decision_reason&&<p className="mt-3 text-sm text-slate-400">Decision: {a.decision_reason}</p>}{a.status==="pending"&&<div className="mt-4 flex gap-2"><button onClick={()=>void decide(a.id,"approve")} className="btn-primary">Approve & execute</button><button onClick={()=>void decide(a.id,"reject")} className="btn-danger">Reject</button></div>}</section>)}{approvals.length===0&&<Empty text="No approval requests yet."/>}</div>}
            {tab==="Audit"&&<div className="card overflow-x-auto"><table className="w-full min-w-[950px] text-left text-sm"><thead className="text-xs uppercase text-slate-500"><tr><th className="pb-3">Time</th><th>Agent</th><th>Tool</th><th>Status</th><th>Risk</th><th>Approval</th><th>Summary</th></tr></thead><tbody>{audit.map(x=><tr key={x.id} className="border-t border-white/5"><td className="py-4 pr-3 text-xs text-slate-500">{new Date(x.created_at).toLocaleString()}</td><td>{x.agent_name||"—"}</td><td>{x.tool_name||"—"}</td><td><span className={`pill ${pill(x.status)}`}>{x.status}</span></td><td>{x.risk_level||"—"}</td><td>{x.approval_status||"—"}</td><td className="max-w-md truncate text-slate-400">{x.error_message||x.output_summary||x.input_summary}</td></tr>)}</tbody></table></div>}
            {tab==="Runner"&&<div className="grid gap-6 xl:grid-cols-2"><section className="card"><h2 className="section-title">Run a governed tool call</h2><label className="label">Agent</label><select className="input" value={runnerAgent} onChange={e=>setRunnerAgent(Number(e.target.value))}>{agents.map(a=><option key={a.id} value={a.id}>{a.name}</option>)}</select><label className="label">Tool</label><select className="input" value={runnerTool} onChange={e=>setRunnerTool(Number(e.target.value))}>{tools.map(t=><option key={t.id} value={t.id}>{t.name} · {t.risk_level}/{t.action_type}</option>)}</select><label className="label">Input</label><textarea className="input min-h-40" value={runnerInput} onChange={e=>setRunnerInput(e.target.value)} /><p className="mt-2 text-xs text-slate-500">GitHub tools expect JSON. Example PR: {`{"owner":"octocat","repo":"Hello-World","pull_number":1}`}</p><button onClick={()=>void runTask()} className="btn-primary mt-4">Run through policy engine</button></section><section className="card"><h2 className="section-title">Governed result</h2>{runnerResult?<pre className="max-h-[600px] overflow-auto whitespace-pre-wrap rounded-xl bg-black/25 p-4 text-xs text-slate-300">{JSON.stringify(runnerResult,null,2)}</pre>:<Empty text="Run a tool to see policy, approval, execution, and audit results."/>}</section></div>}
          </>}
        </div>
      </main>
    </div>
  </div>
}

function AgentCard({agent,tools,onSave}:{agent:Agent;tools:Tool[];onSave:(a:Agent,allowed:string[])=>Promise<void>}){
  const [allowed,setAllowed]=useState<string[]>(agent.allowed_tools); useEffect(()=>setAllowed(agent.allowed_tools),[agent.allowed_tools]);
  const toggle=(name:string)=>setAllowed(v=>v.includes(name)?v.filter(x=>x!==name):[...v,name]);
  return <section className="card"><div className="flex items-start justify-between gap-3"><div><h2 className="text-lg font-semibold">{agent.name}</h2><p className="mt-1 text-sm text-slate-400">{agent.role}</p></div><span className={`pill ${pill(agent.status)}`}>{agent.status}</span></div><div className="mt-5 text-xs font-semibold uppercase tracking-wider text-slate-500">Tool permissions</div><div className="mt-3 grid gap-2 sm:grid-cols-2">{tools.map(t=><label key={t.id} className="flex items-start gap-3 rounded-xl border border-white/5 bg-black/15 p-3"><input type="checkbox" className="mt-1" checked={allowed.includes(t.name)} onChange={()=>toggle(t.name)}/><span><span className="block text-sm font-medium">{t.name}</span><span className="text-xs text-slate-500">{t.risk_level} · {t.action_type}{t.requires_approval?" · approval":""}</span></span></label>)}</div><button onClick={()=>void onSave(agent,allowed)} className="btn-primary mt-4">Save permissions</button></section>
}
function Empty({text}:{text:string}){return <div className="rounded-xl border border-dashed border-white/10 p-6 text-center text-sm text-slate-500">{text}</div>}
export default App;