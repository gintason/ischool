import React from "react";

export default function Terms() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-50 to-white text-gray-800 flex justify-center px-6 py-12">
      <div className="max-w-3xl w-full bg-white rounded-2xl shadow-lg p-8 md:p-12">
        {/* Header */}
        <h1 className="text-3xl md:text-4xl font-bold text-sky-600 mb-6 text-center">
          Terms & Conditions
        </h1>
        <p className="text-center text-gray-600 mb-10">
          Effective Date: <span className="font-semibold">October, 2025</span>
        </p>

        {/* Sections */}
        <div className="space-y-8 text-[15px] leading-relaxed">
          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              1. Acceptance of Terms
            </h2>
            <p>
              By using the iSchool Mobile app, you agree to comply with and be
              bound by these Terms & Conditions. If you do not agree, you must
              discontinue use of the app immediately.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              2. Eligibility
            </h2>
            <p>
              The app is designed for secondary school students (JSS1–SSS3) and
              their guardians. By registering, you confirm that you are eligible
              to use the app.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              3. User Accounts
            </h2>
            <p>
              You are responsible for maintaining the confidentiality of your
              login credentials. Sharing accounts or misusing them may lead to
              suspension or termination.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              4. App Usage
            </h2>
            <p>
              You agree not to:
              <ul className="list-disc ml-6 mt-2 space-y-1">
                <li>Use the app for unlawful or harmful purposes.</li>
                <li>Interfere with or disrupt app functionality.</li>
                <li>Attempt to gain unauthorized access to our systems.</li>
              </ul>
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              5. Intellectual Property
            </h2>
            <p>
              All content, trademarks, and materials in the app belong to
              iSchool Mobile and its licensors. Unauthorized use is prohibited.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              6. Subscription & Payments
            </h2>
            <p>
              Certain features may require payment. By subscribing, you agree to
              our pricing, billing, and refund policies as stated at the time of
              purchase.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              7. Limitation of Liability
            </h2>
            <p>
              iSchool Mobile is not liable for any damages resulting from use of
              the app, including data loss, service interruptions, or misuse of
              information by users.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              8. Termination
            </h2>
            <p>
              We reserve the right to suspend or terminate accounts that violate
              these terms without prior notice.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              9. Changes to Terms
            </h2>
            <p>
              We may update these Terms & Conditions at any time. Updates will
              be posted in-app and/or on our website. Continued use means you
              accept the new terms.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              10. Contact Us
            </h2>
            <p>
              For questions about these Terms & Conditions, contact us at:
              <br />
              📧{" "}
              <a
                href="mailto:support@ischool.ng"
                className="text-sky-600 underline"
              >
                support@ischool.ng
              </a>
            </p>
          </section>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-gray-500 text-sm">
          © {new Date().getFullYear()} iSchool Mobile. All Rights Reserved.
        </div>
      </div>
    </div>
  );
}
