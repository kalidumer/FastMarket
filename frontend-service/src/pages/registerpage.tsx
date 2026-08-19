import {useEffect, useState} from "react";
import { useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector} from "../store/store";
import { registerUser, clearAuthError,loginUser } from "../features/auth/authSlice";
export default function Signup(){

    const dispatch = useAppDispatch();
    const navigate = useNavigate();
    const {loading,token,error}=useAppSelector((state)=>state.auth)

    const [full_name,setFullname]=useState('');
    const[email,setEmail]=useState('');
    const[password,setPassword]=useState('');
    const[confirmPassword,setConfirmPassword]=useState('')
    const[validationError,setValidationError]=useState<string|null>(null);

    useEffect(() => {
     return () =>{
        dispatch(clearAuthError());
     }   
    },[dispatch])

    useEffect(()=>{
        if(token){
            navigate('/',{replace:true})
        }},[token,navigate])


    const handleSunmit=async(e:React.FormEvent)=>{
        e.preventDefault();
        setValidationError(null);

        if(!full_name.trim() || !email.trim() || !password.trim() || !confirmPassword.trim()){
            setValidationError("Please Fill All Required Fields!");
            return;
        }


        if(password.length<6){
            setValidationError("use password min 6 characters long");
            return;
        }

        if(password!==confirmPassword){
            setValidationError("password mistmatch try again");
            return;
        }

        const resultSignup = await dispatch(registerUser({full_name,email,password}));
        if(registerUser.fulfilled.match(resultSignup)){
            dispatch(loginUser({email,password}));
        }

    }

    return(<>
    <div className="flex bg-red-500 min-h-10"></div>
    </>)
}