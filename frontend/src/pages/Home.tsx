import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Home = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const getToken = async () => {
      const accessToken = localStorage.getItem("access_token") || "";
      const refreshToken = localStorage.getItem("refresh_token") || "";

      try {
        const verifyRes = await fetch(
          `http://localhost:8000/verify-token/${accessToken}`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
        if (verifyRes.status === 403 && refreshToken) {
          const refreshRes = await fetch("http://localhost:8000/refresh", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ refresh_token: refreshToken }),
          });

          if (!refreshRes.ok) {
            const err = await refreshRes.json();
            console.error("Refresh error details:", err);
            throw new Error(err.detail || "Refresh token error");
          }

          const data = await refreshRes.json();
          console.log(data);
          localStorage.setItem("access_token", data.access_token);
          console.log("updated local storage");
        } else if (!verifyRes.ok) {
          const err = await verifyRes.json();
          throw new Error(err.detail || "Access token error");
        }
      } catch (err) {
        console.error(err);
        navigate("/login");
      }
    };

    getToken();
  }, [navigate]);

  return <div className="text-white text-lg p-6">🏠 Home Page</div>;
};

export default Home;
