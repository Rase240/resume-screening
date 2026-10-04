'use client';
import {useCallback,useEffect,useMemo,useRef,useState} from 'react';
import {ArrowDownToLine,ArrowRight,Bookmark,ChartNoAxesCombined,Check,ChevronDown,ClipboardList,Clock3,Filter,Menu,Plus,Search,SlidersHorizontal,Trash2,UploadCloud,Users,X} from 'lucide-react';
import RoleForm from '@/components/RoleForm';
import CandidatePanel from '@/components/CandidatePanel';
import {API,Candidate,Role,json,request} from '@/lib/api';

type View='Overview'|'Open roles'|'Candidates'|'Settings';
type UploadResult={filename:string;status:string;message?:string};
const nav:View[]=['Overview','Open roles','Candidates','Settings'];
const statuses=['New','In review','Shortlisted','Rejected'];
const serviceUnavailable=(error:unknown)=>String((error as Error)?.message||error).includes('screening service is unavailable');

export default function Page(){
 const [roles,setRoles]=useState<Role[]>([]);
 const [roleId,setRoleId]=useState('');
 const [candidates,setCandidates]=useState<Candidate[]>([]);
 const [view,setView]=useState<View>('Candidates');
 const [selectedId,setSelectedId]=useState<string|null>(null);
 const [roleForm,setRoleForm]=useState<'new'|'edit'|null>(null);
 const [confirmRoleId,setConfirmRoleId]=useState<string|null>(null);
 const [top,setTop]=useState(10);
 const [query,setQuery]=useState('');
 const [statusFilter,setStatusFilter]=useState('All statuses');
 const [skillFilter,setSkillFilter]=useState('All required skills');
 const [minScore,setMinScore]=useState(0);
 const [sort,setSort]=useState('Score: high to low');
 const [compare,setCompare]=useState<string[]>([]);
 const [showCompare,setShowCompare]=useState(false);
 const [uploading,setUploading]=useState(false);
 const [uploadResults,setUploadResults]=useState<UploadResult[]>([]);
 const [bulkBusy,setBulkBusy]=useState(false);
 const [error,setError]=useState('');
 const [loading,setLoading]=useState(true);
 const [apiOffline,setApiOffline]=useState(false);
 const [mobileNav,setMobileNav]=useState(false);
 const inputRef=useRef<HTMLInputElement>(null);
 const current=roles.find(r=>r.id===roleId);
 const selected=candidates.find(c=>c.id===selectedId)||null;

 const refreshRoles=useCallback(async()=>{const list=await request<Role[]>('/roles');setRoles(list);setRoleId(id=>list.some(x=>x.id===id)?id:(list[0]?.id||''));setApiOffline(false);setError('');return list},[]);
 const refreshCandidates=useCallback(async(id:string)=>{const list=id?await request<Candidate[]>(`/roles/${id}/candidates`):[];setCandidates(list);setApiOffline(false);setError('');setSelectedId(previous=>previous&&list.some(c=>c.id===previous)?previous:(typeof window!=='undefined'&&window.innerWidth>=1400?list[0]?.id||null:null))},[]);
 useEffect(()=>{refreshRoles().catch(e=>{setApiOffline(serviceUnavailable(e));setError(e.message)}).finally(()=>setLoading(false))},[refreshRoles]);
 useEffect(()=>{if(roleId)refreshCandidates(roleId).catch(e=>{if(e.message==='Role not found'){refreshRoles().catch(err=>{setApiOffline(serviceUnavailable(err));setError(err.message)});return}setApiOffline(serviceUnavailable(e));setError(e.message)});else setCandidates([])},[roleId,refreshCandidates,refreshRoles]);
 async function retryConnection(){setLoading(true);try{const list=await refreshRoles();if(list.length)await refreshCandidates(list.some(r=>r.id===roleId)?roleId:list[0].id)}catch(e){setApiOffline(serviceUnavailable(e));setError((e as Error).message)}finally{setLoading(false)}}
 const counts=useMemo(()=>({new:candidates.filter(c=>c.status==='New').length,review:candidates.filter(c=>c.status==='In review').length,shortlisted:candidates.filter(c=>c.status==='Shortlisted').length,strong:candidates.filter(c=>c.match.score>=75).length,average:candidates.length?Math.round(candidates.reduce((sum,c)=>sum+c.match.score,0)/candidates.length):0}),[candidates]);
 const filtered=useMemo(()=>{let result=candidates.filter(c=>{
  const search=`${c.parsed.name} ${c.parsed.email} ${c.parsed.title} ${c.parsed.skills.join(' ')} ${c.text}`.toLowerCase().includes(query.toLowerCase());
  return search&&(statusFilter==='All statuses'||c.status===statusFilter)&&(skillFilter==='All required skills'||c.match.matched.some(s=>s.toLowerCase()===skillFilter.toLowerCase()))&&c.match.score>=minScore;
 });if(sort==='Score: low to high')result=[...result].sort((a,b)=>a.match.score-b.match.score);if(sort==='Name: A to Z')result=[...result].sort((a,b)=>a.parsed.name.localeCompare(b.parsed.name));return result},[candidates,query,statusFilter,skillFilter,minScore,sort]);
 const visible=filtered.slice(0,top);
 const coverage=(current?.required_skills||[]).map(skill=>({skill,count:candidates.filter(c=>c.match.matched.some(s=>s.toLowerCase()===skill.toLowerCase())).length}));

 async function saveRole(value:Omit<Role,'id'>){const path=roleForm==='edit'?`/roles/${roleId}`:'/roles';const saved=await request<Role>(path,json(roleForm==='edit'?'PUT':'POST',value));await refreshRoles();setRoleId(saved.id);await refreshCandidates(saved.id);setView('Candidates');setError('')}
 async function upload(files:FileList|null){if(!files?.length||!roleId)return;setUploading(true);setUploadResults([]);setError('');const form=new FormData();Array.from(files).forEach(f=>form.append('files',f));try{const results=await request<UploadResult[]>(`/roles/${roleId}/upload`,{method:'POST',body:form});setUploadResults(results);await refreshCandidates(roleId)}catch(e){setError((e as Error).message)}finally{setUploading(false);if(inputRef.current)inputRef.current.value=''}}
 async function updateCandidate(id:string,payload:object){try{await request<Candidate>(`/candidates/${id}`,json('PATCH',payload));await refreshCandidates(roleId)}catch(e){setError((e as Error).message);throw e}}
 async function bulkStatus(status:string){if(!compare.length)return;setBulkBusy(true);try{await request(`/roles/${roleId}/candidates/status`,json('PATCH',{ids:compare,status}));setCompare([]);await refreshCandidates(roleId)}catch(e){setError((e as Error).message)}finally{setBulkBusy(false)}}
 async function deleteCandidate(id:string){try{await request(`/candidates/${id}`,{method:'DELETE'});setSelectedId(null);setCompare(ids=>ids.filter(item=>item!==id));await refreshCandidates(roleId)}catch(e){setError((e as Error).message)}}
 async function deleteRole(id:string){try{await request(`/roles/${id}`,{method:'DELETE'});await refreshRoles();setSelectedId(null);setConfirmRoleId(null)}catch(e){setError((e as Error).message)}}
 function openView(label:View){setView(label);setMobileNav(false);if(label==='Candidates')setSelectedId(null)}
 return <main><h1>Folio Screening</h1></main>;
}