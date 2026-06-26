export type ServiceItem = {
  text: string;
};

export type ServiceCard = {
  iconSrc: string; // Path to the icon image or a placeholder
  altText: string;
  title: string;
  price: string;
  items: ServiceItem[];
};

export interface AddOnServicesSectionProps {
  heading: string;
  subheading: string;
  services: ServiceCard[];
}

export interface AddOnsServicesI {
  id: string;
  name: string;
  prices: { amount: number; unit: string; selectedPriceIndex: number }[];
  selectedPriceIndex: number;
}

export interface APIAddOnsServicesI {
  message: string;
  status: string;
  data: {
    id: string;
    name: string;
    prices: { amount: number; unit: string }[];
  }[];
}
