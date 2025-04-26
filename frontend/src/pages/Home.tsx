import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

const Home: React.FC = () => {
  const [chatbotName, setChatbotName] = useState("");
  const [chatbotPrompt, setChatbotPrompt] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState<boolean>(false);
  const [upserting, setUpseting] = useState<boolean>(false);
  const [botToken, setBotToken] = useState<string>('');
  const [copied, setCopied] = useState(false);

  const navigate = useNavigate();
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
      setUpseting(true)
      const token = localStorage.getItem("access_token");
      const res = await fetch("http://localhost:8000/create-chatbot", {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });
      setUpseting(false)
      const data = await res.json();
      setBotToken(data.bot_token)
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
      <div className="absolute top-5 right-5 flex flex-col gap-3">
    <Link to={'/profile'} className="bg-gray-100 px-3 py-1 rounded-2xl shadow-lg shadow-black" >Profile</Link>
    <Link to={'/chat'} className="bg-gray-100 px-3 py-1 rounded-2xl shadow-lg shadow-black" >Test Chat</Link>
      </div>
      {success ? (
        <div className="w-full max-w-md bg-gray-800 p-6 rounded-xl shadow-md text-white text-center space-y-4">
        <h2 className="text-2xl font-bold">🎉 Chatbot Created Successfully!</h2>
        <p className="text-gray-300">Here is your bot token. Copy and save it securely:</p>
        <div className="bg-gray-700 p-4 rounded-md text-sm break-all border border-gray-600">
          {botToken}
        </div>
        <button
          onClick={() => {
            navigator.clipboard.writeText(botToken);
            setCopied(true)
          }}
          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md text-white font-medium transition duration-200"
        >
          {copied ? <p> Copied! </p> : <p>Copy to Clipboard</p>}
        </button>
        <button
          onClick={() => {
            setSuccess(false);
            setBotToken("");
          }}
          className="block w-full mt-4 bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-md text-white transition duration-200"
        >
          Create Another Bot
        </button>
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
            {upserting ? <h1 className="text-white">Creating your chatbot ...</h1> : <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md transition duration-200"
            >
              Create
            </button>}
          </form>
        </div>
      )}
    </div>
  );
};

export default Home;

