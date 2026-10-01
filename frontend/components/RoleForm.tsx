'use client';
import {useEffect,useState} from 'react';
import {X} from 'lucide-react';
import {Role} from '@/lib/api';
const defaults={title:'',description:'',required_skills:[],preferred_skills:[],min_experience:0,education:'',location:'',work_mode:'Hybrid',weights:{'Required skills':35,'Preferred skills':10,Experience:15,Education:10,Location:5,'Language similarity':25}};
export default function RoleForm({role,onClose,onSave}:{role?:Role|null;onClose:()=>void;onSave:(value:Omit<Role,'id'>)=>Promise<void>}){
 const [form,setForm]=useState({...defaults,...role});const [required,setRequired]=useState((role?.required_skills||[]).join(', '));const [preferred,setPreferred]=useState((role?.preferred_skills||[]).join(', '));const [saving,setSaving]=useState(false);const [error,setError]=useState('');
}