// src/utils/auth.jsx
import { jwtDecode } from "jwt-decode";

export function getDecodedUser() {
  const token = localStorage.getItem("accessToken");
  if (!token) return null;

  try {
    const decoded = jwtDecode(token);

    // Check if token has expired
    const isExpired = decoded.exp && decoded.exp * 1000 < Date.now();
    if (isExpired) {
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      return null;
    }

    return decoded;
  } catch (error) {
    console.error("Failed to decode token:", error);
    localStorage.removeItem("accessToken");
    return null;
  }
}

