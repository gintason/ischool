import { useEffect } from "react";

// The full policy is a static page (public/privacy-policy.html) so it can be
// read without JavaScript, e.g. by Google Play's policy checker.
export default function PrivacyPolicy() {
  useEffect(() => {
    window.location.replace("/privacy-policy.html");
  }, []);

  return (
    <p className="text-center py-5">
      Loading our <a href="/privacy-policy.html">Privacy Policy</a>…
    </p>
  );
}
