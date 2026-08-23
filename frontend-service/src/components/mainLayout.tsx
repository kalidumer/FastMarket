import { Outlet, Link } from 'react-router-dom';
import { ThemeToggle } from '../components/themeToggle';
import { useState } from 'react';

interface MainLayoutProps {
    children?: React.ReactNode;
}

export const MainLayout:React.FC<MainLayoutProps>=({children})=>{
const [isMobileOpen, setIsMobileOpen] = useState(false);


  const [isDesktopCollapsed, setIsDesktopCollapsed] = useState(false);

  const toggleDesktopSidebar= () => {
    setIsDesktopCollapsed((prev)=>!prev)
  }
  const toggleMobileSidebar = () =>{
    setIsMobileOpen((prev)=>!prev)
  }
    
    return(
    <div className="min-h-screen flex bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
      
      {isMobileOpen && (
        <div
          onClick={() => setIsMobileOpen(false)}
          className="fixed inset-0 z-40 bg-black/50 lg:hidden transition-opacity"
          aria-hidden="true"
        />
      )}

      <aside
        className={`
          fixed inset-y-0 left-0 z-50 flex flex-col bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300
          lg:static lg:z-auto
          ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'} 
          ${isDesktopCollapsed ? 'lg:w-20' : 'lg:w-64'} 
          w-64
        `}
      >
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200 dark:border-gray-700">
          {(!isDesktopCollapsed || isMobileOpen) && (
            <span className="font-bold text-xl tracking-tight">TaskSphere</span>
          )}

          <button
            onClick={toggleDesktopSidebar}
            className="hidden lg:flex p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400"
            aria-label="Toggle Desktop Sidebar"
          >
            {isDesktopCollapsed ? '➡️' : '⬅️'}
          </button>

          <button
            onClick={() => setIsMobileOpen(false)}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400"
            aria-label="Close Mobile Menu"
          >
            ✕
          </button>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <Link
            to="/dashboard"
            onClick={() => setIsMobileOpen(false)} // Close drawer on navigation
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <span className="text-xl">📊</span>
            {(!isDesktopCollapsed || isMobileOpen) && (
              <span className="font-medium">Dashboard</span>
            )}
          </Link>

          <Link
            to="/tasks"
            onClick={() => setIsMobileOpen(false)}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <span className="text-xl">📋</span>
            {(!isDesktopCollapsed || isMobileOpen) && (
              <span className="font-medium">Tasks</span>
            )}
          </Link>

          <Link
            to="/profile"
            onClick={() => setIsMobileOpen(false)}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <span className="text-xl">👤</span>
            {(!isDesktopCollapsed || isMobileOpen) && (
              <span className="font-medium">Profile</span>
            )}
          </Link>
        </nav>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">

        <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-4 lg:px-6">
          <div className="flex items-center gap-3">
            <button
              onClick={toggleMobileSidebar}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300"
              aria-label="Open Mobile Menu"
            >
              ☰
            </button>
            <h1 className="text-lg font-semibold">Workspace</h1>
          </div>

          <div className="flex items-center gap-4">
            <ThemeToggle />
          </div>
        </header>

        <main className="flex-1 p-4 lg:p-6 overflow-y-auto">
          {children || <Outlet />}
        </main>
      </div>
    </div>
    )
}