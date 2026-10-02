'use client';
import {useEffect,useState} from 'react';
import {Download,ExternalLink,Save,Trash2,X} from 'lucide-react';
import {API,Candidate} from '@/lib/api';
type Tab='Overview'|'Resume'|'Notes';
export default function CandidatePanel({candidate,onClose,onUpdate,onDelete}:{candidate:Candidate;onClose:()=>void;onUpdate:(id:string,payload:object)=>Promise<void>;onDelete:(id:string)=>Promise<void>}){
 const [tab,setTab]=useState<Tab>('Overview');
 const [note,setNote]=useState(candidate.notes);
 const [editing,setEditing]=useState(false);
}