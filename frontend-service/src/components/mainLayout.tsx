import { Outlet, Link } from 'react-router-dom';
import { ThemeToggle } from '../components/themeToggle';

interface MainLayoutProps {
    children?: React.ReactNode;
}

export const MainLayout:React.FC<MainLayoutProps>=({children})=>{

    
    return(
        <div className="min-h-screen flex transition-colors bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-50">
        <aside className='w-64 bg-gray-50 dark:bg-gray-900 flex flex-col border-r-2 border-gray-400'>
        <div className='h-16 flex justify-center items-center border-b-2 border-gray-200 dark:border-gray-400'>
        side sphere
        </div>
        <nav className='flex-1 p-4 space-y-2'>
        <Link to='/dashboard' className='block px-4 py-2 rounded-md hover:bg-amber-100 dark:hover:bg-gray-700 transition-colors'>Dashboard</Link>
        <Link to='/tasks' className='block px-4 py-2 rounded-md hover:bg-amber-100 dark:hover:bg-gray-700 transition-colors'>Tasks</Link>
        <Link to='/profile' className='block px-4 py-2 rounded-md hover:bg-amber-100 dark:hover:bg-gray-700 transition-colors'>Profile</Link>
        </nav>
        </aside>
        <div className='flex flex-col flex-1'>
            <header className='h-16 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 flex items-center justify-content'>
            <h1 className='text-lg font-semibold'>Workspace</h1>
            <div className='flex items-center gap-4'>
                <ThemeToggle/>
            </div>
            </header>
            <main className="flex-1 p-6 overflow-y-auto">
          {children || <Outlet />}
        </main>
        </div>

        </div>
    )
}