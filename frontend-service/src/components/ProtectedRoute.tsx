import {Navigate,Outlet} from 'react-router-dom'
import{useAppSelector} from '../store/store';

export default function ProtectedRoute(){

    const token =useAppSelector((state)=>state.auth)

    if(!token){
        return <Navigate to="/login" replace />
    }

    return <Outlet />
}