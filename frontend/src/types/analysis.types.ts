export interface AnalysisDataProps {
  email: string;
  whatsapp: string;
  startupIdea: string;
  preview: string;
  ideaScore: string;
}

export interface SelectedAddsOnUnit {
  id: string;
  amount: number;
  unit: string;
}

export interface IdeaReply {
  sentReview: boolean;
  prompt: string;
  preview: string;
  ideaScore: string;
  id: string;
  idx?: number;
  canceledPay?: boolean;
}
