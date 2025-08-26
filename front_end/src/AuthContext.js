import React, { createContext, useState, useEffect } from "react";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => {
    const token = localStorage.getItem("token");
    const userRaw = localStorage.getItem("user");
    let user = null;
    if (userRaw && userRaw !== "undefined") {
      try {
        user = JSON.parse(userRaw);
      } catch {
        user = null;
      }
    }
    return token && user ? { token, user } : null;
  });

  useEffect(() => {
    if (auth) {
      localStorage.setItem("token", auth.token);
      localStorage.setItem("user", JSON.stringify(auth.user));
    } else {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    }
  }, [auth]);

  return (
    <AuthContext.Provider value={{ auth, setAuth }}>
      {children}
    </AuthContext.Provider>
  );
}
