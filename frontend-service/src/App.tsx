import Login from "./pages/loginpage";
import {Routes,Route} from "react-router-dom"

export default function App() {
  
  return (
    <>
      <div className="min-h-screen bg-gray-50 text-gray-900 font-sans antialiased">
      <main className="max-w-7xl mx-auto px-4 grid grid-cols-1 lg:grid-cols-3 gap-8 pb-12">
        {/* <TicketForm onSubmitTicket={createNewTicket} error={error} />
        <TicketQueue tickets={tickets} /> */}
        
      </main>
      <Routes>
        <Route path="/login" element={<Login />} />
      </Routes>
    </div>
    </>
  )
}

