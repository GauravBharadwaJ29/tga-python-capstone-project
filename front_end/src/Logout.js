import { useContext } from "react";
import { AuthContext } from "./AuthContext";

export default function Logout() {
  const { setAuth } = useContext(AuthContext);
  return (
    <button onClick={() => setAuth(null)}>
      Logout
    </button>
  );
}
