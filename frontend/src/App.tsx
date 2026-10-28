import { useEffect, useState } from 'react';

type KB = {id:number; name:string; description:string};
type Doc = {id:number; filename:string; chunk_count:number};
type Citation = {document_id:number; filename:string; chunk_id:number; excerpt:string};
type Message = {role:'user'|'assistant'; text:string; citations?:Citation[]; mode?:string};

async function api<T>(url:string, options?:RequestInit):Promise<T> {
  const res=await fetch(url,options);
  if(!res.ok) throw new Error((await res.json().catch(()=>({detail:res.statusText}))).detail || `HTTP ${res.status}`);
  return res.status===204 ? undefined as T : await res.json();
}
const json=(body:unknown):RequestInit=>({method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});

export default function App(){
  const [bases,setBases]=useState<KB[]>([]),[current,setCurrent]=useState<number|null>(null),[docs,setDocs]=useState<Doc[]>([]);
  const [newName,setNewName]=useState(''),[question,setQuestion]=useState(''),[messages,setMessages]=useState<Message[]>([]);
  const [busy,setBusy]=useState(false),[error,setError]=useState('');
  const refresh=()=>api<KB[]>('/api/knowledge-bases').then(items=>{setBases(items);setCurrent(id=>id!==null&&items.some(x=>x.id===id)?id:(items[0]?.id??null));}).catch(e=>setError(e.message));
  useEffect(()=>{refresh();},[]);
  useEffect(()=>{setMessages([]);setDocs([]);if(current!==null)api<Doc[]>(`/api/knowledge-bases/${current}/documents`).then(setDocs).catch(e=>setError(e.message));},[current]);
  async function create(){if(!newName.trim())return;setError('');try{const kb=await api<KB>('/api/knowledge-bases',json({name:newName}));setNewName('');await refresh();setCurrent(kb.id);}catch(e){setError(String(e));}}
  async function upload(file:File){if(current===null)return;setBusy(true);setError('');try{const form=new FormData();form.append('file',file);await api(`/api/knowledge-bases/${current}/documents`,{method:'POST',body:form});setDocs(await api<Doc[]>(`/api/knowledge-bases/${current}/documents`));}catch(e){setError(String(e));}finally{setBusy(false);}}
  async function ask(){if(current===null||!question.trim()||busy)return;const q=question;setQuestion('');setBusy(true);setError('');setMessages(m=>[...m,{role:'user',text:q},{role:'assistant',text:''}]);try{
    const res=await fetch(`/api/knowledge-bases/${current}/chat/stream`,json({question:q}));if(!res.ok)throw new Error(`HTTP ${res.status}`);
    const reader=res.body?.getReader();if(!reader)throw new Error('浏览器不支持流式读取');const decoder=new TextDecoder();let buffer='';
    while(true){const {value,done}=await reader.read();if(done)break;buffer+=decoder.decode(value,{stream:true});const events=buffer.split('\n\n');buffer=events.pop()||'';
      for(const event of events){if(!event.startsWith('data: '))continue;const data=JSON.parse(event.slice(6));setMessages(m=>{const arr=[...m],last={...arr[arr.length-1]};if(data.type==='delta')last.text+=data.text;if(data.type==='done'){last.citations=data.citations;last.mode=data.mode;}arr[arr.length-1]=last;return arr;});}
    }
  }catch(e){setError(String(e));}finally{setBusy(false);}}
  return <div className="layout"><aside><h1>✦ AI Knowledge Hub</h1><p className="sub">知识库与文档问答</p><form onSubmit={e=>{e.preventDefault();void create();}} className="create"><input value={newName} onChange={e=>setNewName(e.target.value)} placeholder="新知识库名称"/><button>创建</button></form><nav>{bases.map(k=><button key={k.id} className={current===k.id?'active':''} onClick={()=>setCurrent(k.id)}>{k.name}</button>)}</nav></aside>
    <main><header><div><span className="eyebrow">WORKSPACE</span><h2>{bases.find(x=>x.id===current)?.name||'创建你的第一个知识库'}</h2></div><span className="pill">MVP v1.0</span></header>
      {error&&<div className="error" role="alert">{error}<button onClick={()=>setError('')}>关闭</button></div>}
      {current===null?<section className="empty">从左侧创建知识库，上传文档后开始提问。</section>:<><section className="documents"><div className="sectionHead"><h3>资料文档</h3><label className="upload">{busy?'处理中…':'+ 上传文档'}<input type="file" accept=".pdf,.docx,.txt,.md" disabled={busy} onChange={e=>{const f=e.target.files?.[0];if(f)void upload(f);e.target.value='';}}/></label></div><p className="hint">支持 PDF、DOCX、TXT、MD，单文件不超过 5 MB</p><div className="chips">{docs.length?docs.map(d=><span className="chip" key={d.id}>📄 {d.filename} · {d.chunk_count} 段</span>):<span className="hint">还没有文档</span>}</div></section>
      <section className="chat"><h3>知识库问答</h3><div className="messages">{messages.length===0?<div className="empty">例如：请总结上传文档的核心观点，并指出资料来源。</div>:messages.map((m,i)=><div key={i} className={'message '+m.role}><div className="role">{m.role==='user'?'你':'AI 助手'}</div><div className="content">{m.text||'正在回答…'}</div>{m.mode==='retrieval_demo'&&<p className="hint">当前为检索演示模式，请在后端配置模型 API Key。</p>}{m.citations?.map((c,j)=><details key={j}><summary>来源 {j+1}：{c.filename}</summary><p>{c.excerpt}</p></details>)}</div>)}</div><form className="ask" onSubmit={e=>{e.preventDefault();void ask();}}><input value={question} onChange={e=>setQuestion(e.target.value)} placeholder="向知识库提问…" disabled={busy}/><button disabled={busy||!question.trim()}>{busy?'处理中':'发送 →'}</button></form></section></>}
    </main></div>;
}
