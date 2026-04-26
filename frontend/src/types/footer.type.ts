// Define the type for a single link
export type LinkItem = {
	label: string;
	href: string;
};

// Define the props for the Footer component
export interface FooterProps {
	quickLinks: LinkItem[];
	companyLinks: LinkItem[];
	contactEmail: string;
	twitterHandle: string;
	facebookHandle: string;
	instagramHandle: string;
	linkedInHandle?: string;
}
