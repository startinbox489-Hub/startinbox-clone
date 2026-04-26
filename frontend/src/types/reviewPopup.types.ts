export interface ReviewData {
	rating: number | null; // 1 to 5
	feedback: string;
}

export interface ReviewPopupProps {
	// A unique ID or reference for the item being reviewed
	idea_id: string;
	// Function called when the user submits or closes the review form
	onClose: (reviewSubmitted: boolean) => void;
	// Function to simulate sending data to a backend API
	sendReviewToBackend: (
		data: ReviewData & { idea_id: string },
	) => Promise<void>;
	// Boolean to control the visibility of the modal
	isOpen: boolean;
}
