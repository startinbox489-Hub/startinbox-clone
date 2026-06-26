export interface PostI {
  id: string;
  title: string;
  date: string;
  image: string;
  content: string;
  shortExcerpt?: string;
  longExcerpt?: string;
}

export interface ApiPostI {
  message: string;
  status: string;
  page: number;
  limit: number;
  pages: number;
  total: number;
  data: PostI[];
}
