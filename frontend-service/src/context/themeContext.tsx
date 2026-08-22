import { useContext,createContext,useEffect,useState } from "react";


type Theme="light" | "dark"

interface ThemeContextType{
    theme:Theme;
    toggleTheme:()=>void;
}

const themeContext=createContext<ThemeContextType |undefined>(undefined);

export const ThemeProvider=({children}:{children:React.ReactNode})=>{
    const [theme,setTheme]=useState<Theme>(()=>{
    const savedTheme=localStorage.getItem('theme') as Theme;

    if (savedTheme) return savedTheme;
    return window.matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light';
    })


useEffect(()=>{
    const root=window.document.documentElement;
    if(theme ==='dark'){
        root.classList.add('dark');
    }else{
        root.classList.remove('dark');
    }

    localStorage.setItem('theme', theme)
},[theme]);

const toggleTheme=()=>{
    setTheme((prev)=> (prev ==='light' ? 'dark' : 'light'));
}

return(
    <themeContext.Provider value={{theme,toggleTheme}}>
        {children}
    </themeContext.Provider>
)}


export const useTheme=()=>{
    const context= useContext(themeContext);
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
}

