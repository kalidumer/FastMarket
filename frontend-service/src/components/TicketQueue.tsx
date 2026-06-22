import { Ticket } from "@/types";
import TicketCard from "./TicketCard";

interface TicketQueueProps {
  tickets: Ticket[];
}

export default function TicketQueue({ tickets }: TicketQueueProps) {
  return (
    <section className="lg:col-span-2 space-y-6">
      {/* QUEUE CONTROLLER HEADER */}
      <div className="flex items-center justify-between border-b pb-3 border-gray-200">
        <h2 className="text-xl font-bold text-slate-800">Agent Ticket Triage Queue</h2>
        <span className="bg-slate-200 text-slate-800 font-semibold text-xs px-2.5 py-1 rounded-full">
          Total Records: {tickets.length}
        </span>
      </div>

      {/* CONDITIONAL RENDER: EMPTY STATE OR ACTIVE CARDS */}
      {tickets.length === 0 ? (
        <div className="bg-white text-center py-12 border border-dashed border-gray-300 rounded-xl text-gray-500 text-sm">
          No tickets recorded inside database. Use the submission panel to generate entry lines!
        </div>
      ) : (
        <div className="space-y-4">
          {tickets.map((ticket) => (
            // Hand off individual records cleanly down into our atomic sub-components
            <TicketCard key={ticket.id} ticket={ticket} />
          ))}
        </div>
      )}
    </section>
  );
}