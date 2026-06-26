"use server";

import { decodeJwt } from "jose";

/**
 * Get JWT header without verification
 * @param {string} token - The JWT token
 * @returns {Object} - The decoded header
 */
export async function getJWTHeader(token: string) {
  try {
    return decodeJwt(token);
  } catch (error) {
    throw new Error(`Failed to decode header: ${(error as Error).message}`);
  }
}
