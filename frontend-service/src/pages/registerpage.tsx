import {useEffect, useState} from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector} from "../store/store";
import { registerUser, clearAuthError,loginUser } from "../features/auth/authSlice";
import Input from "../components/input";
import Button from "../components/button";
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


    const handleSubmit=async(e:React.FormEvent)=>{
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
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
        <div className="w-full max-w-md space-y-8 rounded-xl bg-white shadow-md border border-gray-100 p-4">
            <div className="text-center">
                <h2 className="text-3xl font-bold text-gray-900 tracking-tight">Create Account</h2>
                <p className="mt-2 text-sm text-gray-600">Join the platform to order products</p>
            </div>
            {(validationError || error) &&(
            <div className="rounded-md border border-red-600 bg-red-50 p-4 text-sm text-red-600 transition-all">
<p className="font-medium">{validationError || error}</p>
            </div>)}

            <form onSubmit={handleSubmit} className="space-y-4 mt-8 mx-4">
                <Input 
                placeholder="Enter Your Full Name"
                type="text"
                value={full_name}
                onChange={(e) =>setFullname(e.target.value)}
                />
                <Input
                placeholder="Enter Your Email"
                type="email"
                value={email}
                onChange={(e)=>setEmail(e.target.value)}
                />
                <Input
                placeholder="Create Your Password"
                type="password"
                value={password}
                onChange={(e)=>setPassword(e.target.value)}/>
                <Input
                placeholder="Re-enter Your Password"
                type="password"
                value={confirmPassword}
                onChange={(e)=>setConfirmPassword(e.target.value)}
                />
                <Button type="submit" loading={loading}>
                    Sign Up
                </Button>
            </form>
            <div className="text-center pt-4">
                <p className="text-sm text-gray-600">
                    Already have an account?
                    <Link to="/login" className="font-semibold px-2 text-indigo-500 hover:text-indigo-700">
                    Sign In Here</Link>
                </p>
            </div>
        </div>
    </div>
    </>)
}