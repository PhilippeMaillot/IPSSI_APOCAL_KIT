import { api } from './client';

export type Question = {
  index: number;
  prompt: string;
  options: string[];
  correct_index: number;
};

export type Quiz = {
  id: number;
  title: string;
  source_text: string;
  score: number | null;
  created_at: string;
  questions: Question[];
};

export type QuizSummary = {
  id: number;
  title: string;
  score: number | null;
  nb_questions: number;
  created_at: string;
};

type PaginatedQuizzes = {
  count: number;
  next: string | null;
  previous: string | null;
  results: QuizSummary[];
};

export type AnswerDetail = {
  index: number;
  selected_index: number;
  correct_index: number;
  correct: boolean;
};

export type AnswerResult = {
  score: number;
  total: number;
  details: AnswerDetail[];
};

export async function listQuizzes(): Promise<PaginatedQuizzes> {
  const { data } = await api.get<PaginatedQuizzes>('/quizzes/');
  return data;
}

export async function getQuiz(id: number): Promise<Quiz> {
  const { data } = await api.get<Quiz>(`/quizzes/${id}/`);
  return data;
}

export async function submitAnswers(
  quizId: number,
  answers: { index: number; selected_index: number }[],
): Promise<AnswerResult> {
  const { data } = await api.post<AnswerResult>(`/quizzes/${quizId}/answer/`, { answers });
  return data;
}
