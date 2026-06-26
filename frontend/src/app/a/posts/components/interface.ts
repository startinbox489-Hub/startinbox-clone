export interface IAPostsData {
  message: string;
  status: string;
  page: number;
  limit: number;
  pages: number;
  total: number;
  data: IBlogPost[];
}

export interface IBlogPost {
  id: string;
  title?: string;
  date?: string;
  content?: string;
  image?: string;
  is_draft: boolean;
}

export interface IABlogPostProps {
  page?: string;
  limit?: string;
  blogs: IAPostsData;
}
