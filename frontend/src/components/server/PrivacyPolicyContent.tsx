import React from "react";
import { Mail, Clock, Lock } from "lucide-react";

const PrivacyPolicyContent: React.FC = () => {
  return (
    <div className="text-left max-h-[70vh] overflow-y-auto pr-2">
      {" "}
      {/* Header */}
      <header className="mb-6 border-b pb-2">
        <h1 className="text-2xl font-extrabold text-indigo-700 dark:text-indigo-400 mb-1">
          Startinbox Privacy Policy
        </h1>
        <p className="text-xs text-gray-500 flex items-center space-x-2">
          <span className="flex items-center">
            <Clock className="w-3 h-3 mr-1" /> Effective: Nov 2025
          </span>
          <span className="flex items-center">| Owner: Startinbox</span>
        </p>
      </header>
      {/* 1. Introduction */}
      <section className="mb-4">
        <h2 className="text-lg font-bold text-indigo-600 mb-2">
          1. Introduction
        </h2>
        <p className="text-sm text-gray-700 dark:text-gray-300 leading-snug">
          This policy explains how we collect, use, share, and protect your
          personal information when you use our services. By using Startinbox,
          you <strong>agree to this Privacy Policy</strong>.
        </p>
      </section>
      {/* 2. Information We Collect  */}
      <section className="mb-4">
        <h2 className="text-lg font-bold text-indigo-600 mb-2">
          2. Information We Collect
        </h2>
        <ul className="list-disc list-inside space-y-1 text-sm text-gray-700 dark:text-gray-300 ml-2">
          <li>
            You Provide: name, email, idea details, payment details (not full
            card data).
          </li>
          <li>
            Automatically Collected: Device info, usage data, and Cookies.
          </li>
        </ul>
      </section>
      {/* 3. How We Use Your Information  */}
      <section className="mb-4">
        <h2 className="text-lg font-bold text-indigo-600 mb-2">
          3. How We Use Your Information
        </h2>
        <p className="text-sm text-gray-700 dark:text-gray-300 leading-snug">
          To deliver AI reports, process payments, send updates, and improve
          services. We do not sell your data.
        </p>
      </section>
      {/* 7. Data Storage and Security */}
      <section className="mb-4">
        <h2 className="text-lg font-bold text-indigo-600 mb-2 flex items-center">
          <Lock className="w-4 h-4 mr-2" /> 7. Data Storage and Security
        </h2>
        <p className="text-sm text-gray-700 dark:text-gray-300 leading-snug">
          Data is stored securely using encrypted databases (PostgreSQL, Google
          Cloud) and HTTPS. We comply with GDPR and NDPR standards.
        </p>
      </section>
      {/* 10. Your Data Rights */}
      <section className="mb-4">
        <h2 className="text-lg font-bold text-indigo-600 mb-2">
          10. Your Data Rights
        </h2>
        <p className="text-sm text-gray-700 dark:text-gray-300 leading-snug">
          You have the right to access, correct, or request deletion of your
          data (Right to Be Forgotten). To exercise these rights, email us.
        </p>
      </section>
      {/* 15. Contact Information */}
      <section className="mb-4">
        <h2 className="text-lg font-bold text-indigo-700 mb-2">
          15. Contact Information
        </h2>
        <p className="text-sm text-gray-700 dark:text-gray-300 leading-snug flex items-center">
          <Mail className="w-4 h-4 mr-2" /> support@startinbox.tech
        </p>
      </section>
      {/* TODO: Add more sections from full policy */}
      <p className="text-xs text-center text-gray-400 mt-4">
        For the complete document, please visit the dedicated{" "}
        <a href="/privacy-policy"> privacy-policy </a>
        page after accepting cookies.
      </p>
    </div>
  );
};

export default PrivacyPolicyContent;
