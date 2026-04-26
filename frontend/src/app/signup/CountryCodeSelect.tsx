'use client';

import React, { useState } from 'react';
import countryCodes from '@/staticData/countryCodeData';
import {
	CountryCodeProps,
	CustomDropdownProps,
} from '@/types/countryCode.types';

export function CountryCodeDropdown({
	value,
	handleOnChange,
}: CustomDropdownProps) {
	const [dropdownOpen, setDropdownOpen] = useState(false);

	return (
		<div className="relative">
			<button
				type="button"
				onClick={() => setDropdownOpen(!dropdownOpen)}
				className="inline-flex items-center rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-sm focus:ring-purple-500 focus:border-purple-500 p-3"
			>
				{value}
			</button>

			{dropdownOpen && (
				<div className="absolute z-10 top-full left-0 mt-1 w-48 bg-white border border-gray-300 rounded-md shadow-lg overflow-y-auto max-h-48 text-gray-500">
					{countryCodes.map((country, index) => (
						<div
							key={index}
							onClick={() => {
								handleOnChange(country.code);
								setDropdownOpen(false);
							}}
							className="p-2 cursor-pointer hover:bg-gray-100"
						>
							{country.code} ({country.country})
						</div>
					))}
				</div>
			)}
		</div>
	);
}

export default function CountryCodeSelect({
	value,
	handleOnChange,
}: CountryCodeProps) {
	return (
		<select
			id="countryCode"
			name="countryCode"
			value={value}
			onChange={handleOnChange}
			className="inline-flex items-center rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-sm focus:ring-purple-500 focus:border-purple-500"
		>
			{countryCodes.map((country, index) => (
				<option key={index} value={country.code}>
					{country.code} ({country.country})
				</option>
			))}
		</select>
	);
}
