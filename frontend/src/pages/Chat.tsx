import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Chat = () => {
  const navigate = useNavigate();
  const [chat_token, setChatToken] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [prompt, setPrompt] = useState<string>("");
  const [response, setResponse] = useState<string>("");

  useEffect(() => {
    const getToken = async () => {
      const accessToken = localStorage.getItem("access_token") || "";
      const refreshToken = localStorage.getItem("refresh_token") || "";
      try {
        const verifyRes = await fetch(
          `http://localhost:8000/users/verify-token/${accessToken}`,
          { method: "GET", headers: { "Content-Type": "application/json" } }
        );
        if (verifyRes.status === 403 && refreshToken) {
          const refreshRes = await fetch("http://localhost:8000/users/refresh", {
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
    getToken();
  }, [navigate]);

  const getResponse = async () => {
    if (prompt && chat_token) {
        setLoading(true)
      const res = await fetch("http://localhost:8000/chatbots/test-chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: prompt,
          chat_token: chat_token,
        }),
      });
      setLoading(false)
      const data = await res.json();
      setResponse(data.content || "No response");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-slate-700 flex flex-col items-center justify-center p-6 shadow-2xl shadow-black">
      <div className="bg-gray-800 shadow-xl rounded-3xl p-8 w-full max-w-2xl text-white">
        <h1 className="text-3xl font-bold text-center mb-6">🤖 Chatbot</h1>

        <div className="flex flex-col gap-4">
          <input
            type="text"
            placeholder="Chatbot Token"
            className="px-4 py-2 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400"
            onChange={(e) => setChatToken(e.target.value)}
            value={chat_token}
          />
          <input
            type="text"
            placeholder="Please enter your prompt"
            className="px-4 py-2 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400"
            onChange={(e) => setPrompt(e.target.value)}
            value={prompt}
          />
         {loading? <div className="flex items-center justify-center bg-blue-500 text-white font-semibold py-2 rounded-xl">
            Generating Response
         </div> :  <button
            onClick={getResponse}
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-xl transition duration-300"
          >
            Generate
          </button>}
        </div>

        {response && (
          <div className="mt-8 p-4 bg-gray-900 rounded-xl border border-gray-200">
            <h2 className="text-lg font-semibold text-white mb-2">Response:</h2>
            <p className="text-white whitespace-pre-wrap">{response}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;
