"use client";

import React from "react";
import {
  ApiValidationResponseI,
  ApiVerifyPayResponseI,
} from "@/types/paymentVerification.types";

export class PaymentUtil {
  /**
   * Saves pending transaction to local storage on unexpected signout
   *
   * @param txReference provider reference
   * @param paymentReference custom reference
   * @param status status for flutterwave
   * @param success success for stripe
   * @param canceled canceled for stripe
   */
  static saveToLocalStorage(
    key: string,
    data: Record<
      string,
      string | number | null | undefined | object[] | boolean
    >,
  ) {
    localStorage.setItem(key, JSON.stringify(data));
  }

  static removeFromLocalStorage(key: string) {
    localStorage.removeItem(key);
  }
  static getFromLocalStorage(key: string) {
    try {
      const data = localStorage.getItem(key);

      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error(error);
      return null;
    }
  }

  static async sendIdeaToBackend(
    planId: string,
    prompt: string,
  ): Promise<ApiValidationResponseI> {
    try {
      const response = await fetch("/api/v1/validateidea", {
        body: JSON.stringify({
          plan_id: planId,
          prompt,
        }),
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        method: "POST",
      });

      const data: ApiValidationResponseI = await response.json();
      return data;
    } catch (error) {
      console.error("Backend verification error:", error);
      // Treat any backend network/server error as a 'failed' status
      return {
        idea: null,
        status: "failed",
        message:
          "An error occurred during verification. Please try again or contact support.",
      };
    }
  }

  /**
   * Sends payment verification payload to the backend
   * @param provider
   * @param tx_reference
   * @param payment_reference
   * @param gen_pdf
   * @returns {ApiVerifyPayResponseI}
   */
  static async sendVerificationToBackend(
    provider: string, // provider name
    tx_reference: string, // provider payment identifier
    payment_reference: string, // custom payment identifier
    gen_pdf: boolean = false,
  ): Promise<ApiVerifyPayResponseI> {
    try {
      const response = await fetch("/api/v1/payments/verify", {
        body: JSON.stringify({
          payment_reference,
          tx_reference,
          provider,
          gen_pdf,
        }),
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        method: "POST",
      });
      const data: ApiVerifyPayResponseI = await response.json();
      console.log("payment verification data: ", data);

      return data;
    } catch (error) {
      console.error("Backend verification error:", error);
      // Treat any backend network/server error as a 'failed' status
      return {
        data: { status: "failed" },
        status: "failed",
        message:
          "An error occurred during verification. Please try again or contact support.",
      };
    }
  }
}
