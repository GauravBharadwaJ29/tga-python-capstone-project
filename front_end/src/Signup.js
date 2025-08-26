import React, { useState, useContext } from "react";
import { AuthContext } from "./AuthContext";

export default function Signup() {
  const { setAuth } = useContext(AuthContext);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState(""); // <-- use setUsername
  const [error, setError] = useState("");

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await fetch("http://localhost:8080/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, username }),
      });
      if (!res.ok) throw new Error("Signup failed");
      const data = await res.json();
      setAuth({ token: data.token, user: data.user });
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <form onSubmit={handleSignup}>
      <h2>Signup</h2>
      <input
        value={username}
        onChange={e => setUsername(e.target.value)} // <-- fix here
        placeholder="Username"
      /><br/>
      <input
        value={email}
        onChange={e => setEmail(e.target.value)}
        placeholder="Email"
      /><br/>
      <input
        type="password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        placeholder="Password"
      /><br/>
      <button type="submit">Signup</button>
      {error && <div style={{ color: "red" }}>{error}</div>}
    </form>
  );
}
