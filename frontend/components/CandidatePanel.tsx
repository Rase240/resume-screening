'use client';
import {useEffect,useState} from 'react';
import {Download,ExternalLink,Save,Trash2,X} from 'lucide-react';
import {API,Candidate} from '@/lib/api';
type Tab='Overview'|'Resume'|'Notes';
export default function CandidatePanel({candidate,onClose,onUpdate,onDelete}:{candidate:Candidate;onClose:()=>void;onUpdate:(id:string,payload:object)=>Promise<void>;onDelete:(id:string)=>Promise<void>}){
 const [tab,setTab]=useState<Tab>('Overview');
 const [note,setNote]=useState(candidate.notes);
 const [editing,setEditing]=useState(false);
 const [text,setText]=useState(candidate.text);
 const [parsed,setParsed]=useState(candidate.parsed);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState('');
 const [confirmDelete,setConfirmDelete]=useState(false);
 useEffect(()=>{setTab('Overview');setNote(candidate.notes);setText(candidate.text);setParsed(candidate.parsed);setEditing(false);setConfirmDelete(false)},[candidate.id,candidate.notes,candidate.text]);
 async function save(payload:object){setBusy(true);setError('');try{await onUpdate(candidate.id,payload);setEditing(false)}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
}