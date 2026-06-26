export type Step = {
  number: number;
  title: string;
  description: string;
};

export interface HowItWorksSectionProps {
  heading: string;
  subheading: string;
  steps: Step[];
  ctaButtonText: string;
  ctaButtonLink: string;
  ctaSubtext: string;
}
