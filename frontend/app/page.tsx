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

 return <main><h1>Folio Screening</h1></main>;
}