import React from "react";

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-50 to-white text-gray-800 flex justify-center px-6 py-12">
      <div className="max-w-3xl w-full bg-white rounded-2xl shadow-lg p-8 md:p-12">
        {/* Header */}
        <h1 className="text-3xl md:text-4xl font-bold text-sky-600 mb-6 text-center">
          Privacy Policy
        </h1>
        <p className="text-center text-gray-600 mb-10">
          Effective Date: <span className="font-semibold">October, 2025</span>
        </p>

        {/* Sections */}
        <div className="space-y-8 text-[15px] leading-relaxed">
          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              1. Information We Collect
            </h2>
            <p>
              We may collect the following information:
              <ul className="list-disc ml-6 mt-2 space-y-1">
                <li>Account information: email, username, and password.</li>
                <li>Usage data: test results, selected subjects, progress.</li>
                <li>Device details: OS version, app version, basic diagnostics.</li>
              </ul>
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              2. How We Use Information
            </h2>
            <p>
              We use your information to enable app features such as login,
              tests, and result delivery, as well as to improve the user
              experience. We do <span className="font-semibold">not sell</span>{" "}
              your personal data.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              3. Data Sharing
            </h2>
            <p>
              We may share limited data only:
              <ul className="list-disc ml-6 mt-2 space-y-1">
                <li>If required by law.</li>
                <li>
                  With trusted service providers (e.g., email delivery) solely
                  to operate the app.
                </li>
              </ul>
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              4. Data Security
            </h2>
            <p>
              We implement industry-standard security measures to protect your
              data, but no system is completely secure. Use the app at your own
              risk.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              5. Children’s Privacy
            </h2>
            <p>
              The app is intended for secondary school students (JSS1–SSS3). We
              encourage parents and guardians to monitor app usage.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              6. Your Rights
            </h2>
            <p>
              You may request to access or delete your account data at any time.
              Contact us at:{" "}
              <a
                href="mailto:support@ischool.com.ng"
                className="text-sky-600 underline"
              >
                support@ischool.ng
              </a>
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              7. Changes to this Policy
            </h2>
            <p>
              We may update this Privacy Policy from time to time. Updates will
              be posted within the app and/or on our website.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-sky-500 mb-2">
              8. Contact Us
            </h2>
            <p>
              If you have questions about this Privacy Policy, contact us:
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
