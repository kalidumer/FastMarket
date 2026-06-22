import { useState,useEffect } from "react"
import TicketForm from "./components/TicketForm"
import TicketQueue from "./components/TicketQueue"

import { TicketCreatePayload ,GetTicketsResponse, Ticket} from "@/types";
import Header from "./components/Header";

function App() {
  
  const [tickets,setTicket]=useState<Ticket[]>([])
  const [error,setError]=useState<string | null>(null)

  const API_BASE_URL="http://127.0.0.1:8007/api"

  const fetchTickets =async()=>{

    try {
      const response=await fetch("http://127.0.0.1:8007/api/get_tickets")
      if(!response.ok) throw new Error("UNABLE TO FETCH THE DATA FROM BACKEND")

      const data:GetTicketsResponse=await response.json()
      setTicket(data.tickets)

    } catch (err) {
      setError(err instanceof Error ? err.message:"UNKNOWN INTERFACE ERROR!")
    }
  }
      //when fetch new data 

      useEffect(() => {
  // 🟢 Self-executing wrapper isolating the async execution lifecycle
  (async () => {
    try {
      await fetchTickets();
    } catch (err) {
      console.error("IIFE execution catch:", err);
    }
  })();

  const interval = setInterval(() => {
    void fetchTickets();
  }, 4000);

  return () => clearInterval(interval);
}, []);

    // to integrate ticket registeration

  const createNewTicket=async(payload:TicketCreatePayload)=>{
  setError(null);

  try {

    const response=await fetch(`${API_BASE_URL}/create_ticket`,{
      method:"POST",
      headers:{"content-type": "application/json"},
      body:JSON.stringify(payload)
    })

    if(!response.ok) throw new Error("unable to fetch to register!")
      await fetchTickets()
  } catch (err) {
    setError(err instanceof Error ? err.message : "Unable to register the ticket!")
    throw err
  }

  }
  return (
    <>

      <div className="min-h-screen bg-gray-50 text-gray-900 font-sans antialiased">
      {/* 1. Header component layer */}
      <Header />

      {/* CORE FRAME GRID SYSTEM */}
      <main className="max-w-7xl mx-auto px-4 grid grid-cols-1 lg:grid-cols-3 gap-8 pb-12">
        {/* 2. Form component running on native form action lifecycles */}
        <TicketForm onSubmitTicket={createNewTicket} error={error} />

        {/* 3. Live real-time dashboard queue component mapping over synchronized types */}
        <TicketQueue tickets={tickets} />
      </main>
    </div>
    </>
  )
}


export default App
