import CButton from "./components/button";
import Input from "./components/input";
import Login from "./pages/loginpage";
import {Routes,Route} from "react-router-dom"
import Header from "./components/Header"

export default function App() {
  
  return (
    <>
      <div className="min-h-screen bg-gray-50 text-gray-900 font-sans antialiased">
      <main className="max-w-7xl mx-auto px-4 grid grid-cols-1 lg:grid-cols-3 gap-8 pb-12">
        {/* <TicketForm onSubmitTicket={createNewTicket} error={error} />
        <TicketQueue tickets={tickets} /> */}
        <Header />
      </main>
      <Routes>
        {/* <Route path="/login" element={<Login />} /> */}
      </Routes>
    </div>
    </>
  )
}

