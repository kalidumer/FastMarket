export interface Ticket {
  id: number;
  customer_name: string;
  feedback_text: string;
  urgency_level: string;      
  customer_sentiment: string; 
  suggested_action: string;   
  draft_reply: string;       
  created_at: string;        
}

export interface GetTicketsResponse {
  total_count: number;
  tickets: Ticket[];
}

export interface TicketCreatePayload {
  customer_name: string;
  feedback_text: string;
}