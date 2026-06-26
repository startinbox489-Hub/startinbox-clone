import { useState, useEffect, useCallback } from "react";

const COOKIE_KEY = "startinbox_cookieConsent";
const ONE_YEAR_IN_MS = 365 * 24 * 60 * 60 * 1000;

/**
 * Custom hook to manage cookie consent state and persistence.
 * @returns {boolean} isConsentGiven - True if the user has accepted, false otherwise.
 * @returns {function} giveConsent - Function to set the consent and store it for 1 year.
 * @returns {boolean} isBannerVisible - True if the banner should be rendered.
 */
export const useCookieConsent = () => {
  const [isConsentGiven, setIsConsentGiven] = useState<boolean | null>(null);

  // Check for existing consent when the component mounts
  useEffect(() => {
    const storedConsent = localStorage.getItem(COOKIE_KEY);
    const expirationTime = storedConsent ? JSON.parse(storedConsent).expiry : 0;
    const now = new Date().getTime();

    if (expirationTime > now) {
      // Consent is valid and not expired
      setIsConsentGiven(true);
    } else {
      // Consent is expired or doesn't exist
      setIsConsentGiven(false);
      localStorage.removeItem(COOKIE_KEY);
    }
  }, []);

  // Function to set consent when the user clicks 'Accept'
  const giveConsent = useCallback(() => {
    const expiryDate = new Date().getTime() + ONE_YEAR_IN_MS;

    localStorage.setItem(
      COOKIE_KEY,
      JSON.stringify({
        value: true,
        expiry: expiryDate,
      }),
    );
    setIsConsentGiven(true);

    location.reload(); // required for META Pixel
  }, []);

  // Banner is visible only when   consent is checked (not null) AND consent is false
  const isBannerVisible = isConsentGiven === false;

  return { isConsentGiven, giveConsent, isBannerVisible };
};
