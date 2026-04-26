export interface CountryCodeI {
	country: string;
	code: string;
}

export interface CountryCodeProps {
	value: string;
	handleOnChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
}

export interface CustomDropdownProps {
	value: string;
	handleOnChange: (value: string) => void;
}
