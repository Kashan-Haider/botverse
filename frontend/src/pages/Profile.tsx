import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Profile = () => {
  const navigate = useNavigate();
  const accessToken = localStorage.getItem("access_token") || "";
  const refreshToken = localStorage.getItem("refresh_token") || "";

  const [userData, setUserData] = useState<null | {
    user: { id: number; username: string; email: string };
    chatbots: { id: number; name: string; prompt: string; token: string }[];
  }>(null);

  useEffect(() => {
    const getUser = async () => {
      const getToken = async () => {
        try {
          const verifyRes = await fetch(
            `http://localhost:8000/users/verify-token/${accessToken}`,
            { method: "GET", headers: { "Content-Type": "application/json" } }
          );
          if (verifyRes.status === 403 && refreshToken) {
            const refreshRes = await fetch("http://localhost:8000/refresh", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ refresh_token: refreshToken }),
            });
            if (!refreshRes.ok) throw new Error("Refresh token error");
            const data = await refreshRes.json();
            localStorage.setItem("access_token", data.access_token);
          } else if (!verifyRes.ok) {
            throw new Error("Access token error");
          }
        } catch (err) {
          navigate("/login");
        }
      };
      await getToken();

      try {
        const response = await fetch("http://localhost:8000/users/current-user", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
        });
        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.detail || "Request failed");
        }

        const data = await response.json();
        setUserData(data);
      } catch (err: any) {
        console.log(err);
      }
    };

    getUser();
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white px-4 py-10">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">User Profile</h1>

        {userData ? (
          <>
            {/* User Card */}
            <div className="bg-gray-800 rounded-2xl p-6 shadow-lg mb-10">
              <h2 className="text-xl font-semibold mb-2">User Info</h2>
              <p><span className="font-semibold">Username:</span> {userData.user.username}</p>
              <p><span className="font-semibold">Email:</span> {userData.user.email}</p>
            </div>

            {/* Chatbots */}
            <h2 className="text-2xl font-semibold mb-4">Your Chatbots</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {userData.chatbots.map((bot) => (
                <div
                  key={bot.id}
                  className="bg-gray-800 p-5 rounded-2xl shadow-md hover:shadow-xl transition duration-300"
                >
                  <h3 className="text-xl font-semibold mb-2">Name: {bot.name}</h3>
                  <p className="mb-2">Prompt: {bot.prompt}</p>
                  <div className=" text-gray-400 break-all">
                    <strong>Token:</strong> {bot.token}
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="text-center text-gray-400">Loading...</div>
        )}
      </div>
    </div>
  );
};

export default Profile;
