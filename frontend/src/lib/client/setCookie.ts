'use client';

import React from 'react';
import Cookies from 'js-cookie';

class CustomCookieUtil {
	static setCookie(
		name: string,
		value: string,
		date: { days?: number; hours?: number; mins?: number },
	) {
		const expires = new Date();
		if (date?.days) expires.setDate(expires.getDate() + date.days);
		if (date?.mins) expires.setDate(expires.getDate() + date.mins);
		if (date?.hours) expires.setDate(expires.getDate() + date.hours);

		Cookies.set(name, value, {
			expires: expires,
			sameSite: 'lax',
			path: '/',
		});
	}

	static clearCookie(name: string) {
		Cookies.remove(name);
	}

	static getCookie(name: string): string | undefined {
		return Cookies.get(name);
	}
}

export default CustomCookieUtil;
