import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [chatbotName, setChatbotName] = useState("");
  const [chatbotPrompt, setChatbotPrompt] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState<boolean>(false);
  const [botToken, setBotToken] = useState<string>('');

  useEffect(() => {
    const getToken = async () => {
      const accessToken = localStorage.getItem("access_token") || "";
      const refreshToken = localStorage.getItem("refresh_token") || "";
      try {
        const verifyRes = await fetch(
          `http://localhost:8000/verify-token/${accessToken}`,
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
    getToken();
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file to upload.");
      return;
    }
    setError("");
    try {
      const formData = new FormData();
      formData.append("chatbot_name", chatbotName);
      formData.append("chatbot_prompt", chatbotPrompt);
      formData.append("file", file);
      const token = localStorage.getItem("access_token");
      const res = await fetch("http://localhost:8000/create-chatbot", {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });
      console.log(res);
      const data = await res.json();
      setBotToken(data)
      if (!res.ok) throw new Error(data.detail || "Failed to create chatbot.");
      setSuccess(true);
      setChatbotName("");
      setChatbotPrompt("");
      setFile(null);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
      {success ? (
        <div className="text-white">
          <h1>Your bot token</h1>
          {botToken}
        </div>
      ) : (
        <div className="w-full max-w-lg bg-gray-800 p-8 rounded-xl shadow-md">
          <h2 className="text-3xl font-bold text-white mb-6 text-center">
            Create Chatbot
          </h2>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-gray-300 mb-1">Chatbot Name</label>
              <input
                type="text"
                value={chatbotName}
                onChange={(e) => setChatbotName(e.target.value)}
                required
                className="w-full px-4 py-2 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-gray-300 mb-1">Chatbot Prompt</label>
              <textarea
                value={chatbotPrompt}
                onChange={(e) => setChatbotPrompt(e.target.value)}
                required
                rows={4}
                className="w-full px-4 py-2 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-gray-300 mb-1">
                Upload Text File
              </label>
              <input
                type="file"
                accept=".txt"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                required
                className="w-full px-1 py-2 rounded-md bg-gray-200 text-gray-900"
              />
            </div>
            {error && <p className="text-red-400 text-sm">{error}</p>}
            {success && <p className="text-green-400 text-sm">{success}</p>}
            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md transition duration-200"
            >
              Create
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default Home;
