export interface SearchPageProps {
  searchParams: Promise<{
    q: string;
  }>;
}
