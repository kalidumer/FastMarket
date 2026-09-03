import Login from "./pages/loginpage";
import {Routes,Route} from "react-router-dom"
import Signup from "./pages/registerpage";
import {Home} from "./pages/home";
import { MainLayout } from "./components/mainLayout";
import ProtectedRoute from "./components/ProtectedRoute";
export default function App() {
  
  return (
    <>
      {/* <div className="min-h-screen bg-gray-50 text-gray-900 font-sans antialiased">
      <main className="max-w-7xl mx-auto px-4 grid grid-cols-1 lg:grid-cols-3 gap-8 pb-12">
      <TicketForm onSubmitTicket={createNewTicket} error={error} />
        <TicketQueue tickets={tickets} /> 
        <Header />
      </main>
      </div> */}
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup/>} /> 

        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout/>}>
            <Route path="/" element={<Home/>} />
          </Route>
        </Route>
      </Routes>
    </>
  )
}

