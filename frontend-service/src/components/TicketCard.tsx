import { Ticket } from "@/types";

interface TicketCardProps{
    ticket:Ticket;
}

export default function TicketCard({ticket}:TicketCardProps){

    const getUrgencyClass=(level:string)=>{
        switch (level?.toLowerCase()) {
      case "high": return "bg-red-100 text-red-800 border-red-200";
      case "medium": return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "low": return "bg-green-100 text-green-800 border-green-200";
      default: return "bg-gray-100 text-gray-500 animate-pulse";
    }
    }


    return(
        <>
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 hover:border-gray-300 transition">
      {/* TOP CARD LINE ROW */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
        <div>
          <h3 className="font-bold text-lg text-slate-900">{ticket.customer_name}</h3>
          <p className="text-xs text-gray-400">
            Ticket ID: #{ticket.id} • {new Date(ticket.created_at).toLocaleString()}
          </p>
        </div>
        {/* COLOR CODED URGENCY BADGE */}
        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getUrgencyClass(ticket.urgency_level)}`}>
          Urgency: {ticket.urgency_level}
        </span>
      </div>

      {/* USER FEEDBACK TEXT CAPTURE */}
      <div className="bg-slate-50 p-3 rounded-lg text-sm text-gray-700 mb-4 border-l-4 border-slate-400 italic">
        "{ticket.feedback_text}"
      </div>

      {/* AI INSIGHT METADATA DISPLAY MATRICES */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
        <div className="text-sm">
          <span className="block font-semibold text-slate-500 text-xs tracking-wider uppercase mb-0.5">Customer Sentiment</span>
          <p className={`font-medium ${ticket.customer_sentiment === 'Processing...' ? 'text-gray-400 animate-pulse' : 'text-slate-800'}`}>
            {ticket.customer_sentiment}
          </p>
        </div>
        <div className="text-sm">
          <span className="block font-semibold text-slate-500 text-xs tracking-wider uppercase mb-0.5">Suggested Actions</span>
          <p className={`font-medium ${ticket.suggested_action === 'Processing...' ? 'text-gray-400 animate-pulse' : 'text-slate-800'}`}>
            {ticket.suggested_action}
          </p>
        </div>
      </div>

      {/* AI PRE-DRAFTED REPLY ACCORDION TABBOX */}
      <div className="mt-4 border-t pt-4 border-gray-100">
        <span className="block font-semibold text-slate-500 text-xs tracking-wider uppercase mb-1">AI Generated Draft Reply Email</span>
        <div className={`p-3 rounded-lg text-sm font-mono whitespace-pre-line ${
          ticket.draft_reply === 'Processing...' 
            ? 'bg-gray-50 text-gray-400 animate-pulse border border-dashed border-gray-200' 
            : 'bg-cyan-50 text-cyan-900 border border-cyan-100'
        }`}>
          {ticket.draft_reply}
        </div>
      </div>
    </div>
            </>
    )
}
