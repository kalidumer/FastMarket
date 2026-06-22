import { TicketCreatePayload } from "@/types";
import React, { useState, useTransition } from "react";


interface ticketFormProps{

onSubmitTicket:(payload:TicketCreatePayload)=>Promise<void>;
error:string|null

}

export default function TicketForm({onSubmitTicket,error}:ticketFormProps){

    const[customerName,setCustomerName]=useState("")
    const[customerFeedback,setCustomerFeedback]=useState("")

// to handle loading
  const [isPending, startTransition] = useTransition();


  const handleFormAction = () => {
    if (!customerName.trim() || !customerFeedback.trim()) return;

    
    startTransition(async () => {
      try {
        await onSubmitTicket({ 
          customer_name: customerName, 
          feedback_text: customerFeedback 
        });
        
        // Reset states on successful submission
        setCustomerName("");
        setCustomerFeedback("");
      } catch (err) {
        console.error("Action submission failed:", err);
      }
    });
  };
    return(
    <>
    <form action={handleFormAction} className="bg-white p-6 rounded-xl border border-gray-200 space-y-4 h-fit shadow-sm">
      <h2 className="text-xl font-bold text-slate-800">Submit Feedback</h2>
      
      {error && (
        <div className="text-red-600 text-sm bg-red-50 p-2.5 rounded-lg border border-red-100">
          ⚠️ {error}
        </div>
      )}
      
      <input
        type="text"
        value={customerName}
        onChange={(e) => setCustomerName(e.target.value)}
        placeholder="Customer Name"
        className="w-full p-2 border border-gray-300 rounded-lg text-sm focus:outline-slate-500"
        required
        disabled={isPending}
      />
      
      <textarea
        value={customerFeedback}
        onChange={(e) => setCustomerFeedback(e.target.value)}
        placeholder="Feedback description..."
        rows={4}
        className="w-full p-2 border border-gray-300 rounded-lg text-sm focus:outline-slate-500"
        required
        disabled={isPending}
      />
      
      <button 
        type="submit" 
        disabled={isPending}
        className="w-full bg-slate-800 hover:bg-slate-700 text-white p-2 rounded-lg text-sm font-bold transition disabled:opacity-50 cursor-pointer"
      >
        {isPending ? "Submitting..." : "Submit Ticket"}
      </button>
    </form>
    </>)

}