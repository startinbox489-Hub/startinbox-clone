export type Item = {
  text: string;
};

export type FeatureCard = {
  iconSrc: string; // Path to SVG or image icon
  altText: string;
  title: string;
  description: string;
  items: Item[]; // List of bullet points
};

export interface AllInOnePlatformSectionProps {
  heading: string;
  subheading: string;
  featureCards: FeatureCard[];
}
