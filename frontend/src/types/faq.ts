export type FAQItem = {
  question: string;
  answer: string;
};

export interface FAQsSectionProps {
  heading: string;
  subheading: string;
  faqs: FAQItem[];
}
