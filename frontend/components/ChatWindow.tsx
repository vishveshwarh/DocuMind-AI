"use client";
import { useState, useRef, useEffect } from "react";

type Message = {
    role: "user" | "bot";
    text: string;
};

export default function ChatWindow() {
    const DEMO_ACCESS_KEY = process.env.NEXT_PUBLIC_DEMO_ACCESS_KEY || "";
    console.log("Using API URL:", process.env.NEXT_PUBLIC_API_URL);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [ready, setReady] = useState(false);
    const [fileName, setFileName] = useState("");
    const fileRef = useRef<HTMLInputElement>(null);
    const bottomRef = useRef<HTMLDivElement>(null);
    const [darkMode, setDarkMode] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api/v1";

    const uploadPDF = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setUploading(true);
        setReady(false);
        setError("");
        setFileName(file.name);

        const form = new FormData();
        form.append("file", file);

        try {
            const res = await fetch(`${API_URL}/documents/upload`, {
                method: "POST",
                headers: {
                    "X-Demo-Key": DEMO_ACCESS_KEY,
                },
                body: form,
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.detail || data.error || "Upload failed");
            }

            setMessages([
                {
                    role: "bot",
                    text: `✅ ${data.message || "PDF uploaded successfully. Ready to chat!"}`,
                },
            ]);

            setReady(true);
            setError("");
        } catch (err) {
            const message = err instanceof Error ? err.message : "Upload failed";

            setReady(false);
            setError(message);
            setMessages([
                {
                    role: "bot",
                    text: `❌ ${message}`,
                },
            ]);

            if (fileRef.current) {
                fileRef.current.value = "";
            }
        } finally {
            setUploading(false);
        }
    };

    const sendMessage = async () => {
        if (!input.trim() || !ready || loading) return;

        const question = input.trim();

        // Add user message immediately — don't wait for API (optimistic UI)
        setMessages(prev => [...prev, { role: "user", text: question }]);
        setInput("");
        setLoading(true);

        try {
            const res = await fetch(`${API_URL}/chat`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Demo-Key": DEMO_ACCESS_KEY,
                },
                body: JSON.stringify({ question }),
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.detail || data.error || "Chat request failed");
            }

            setMessages(prev => [
                ...prev,
                {
                    role: "bot",
                    text: data.answer || "I could not generate an answer.",
                },
            ]);
        } catch (err) {
            const message = err instanceof Error ? err.message : "Error. Is the backend running?";

            setMessages(prev => [
                ...prev,
                {
                    role: "bot",
                    text: `❌ ${message}`,
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={`min-h-screen flex flex-col items-center py-6 px-3 sm:py-10 sm:px-4 transition-colors duration-300
  ${darkMode ? "bg-gray-900 text-white" : "bg-gray-50 text-gray-900"}`}>


            <div className="w-full max-w-2xl mb-4 flex justify-between items-center">
                {/* App header */}
                <div>
                    <h1 className="text-2xl font-semibold">DocuMind-AI</h1>
                    <p className={`text-sm mt-1 ${darkMode ? "text-gray-400" : "text-gray-500"}`}>
                        Upload a PDF and ask questions about it
                    </p>
                </div>
                {/* Dark/Light toggle button */}
                <button
                    onClick={() => setDarkMode(!darkMode)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors
                                ${darkMode
                            ? "bg-gray-700 text-yellow-300 hover:bg-gray-600"
                            : "bg-gray-200 text-gray-700 hover:bg-gray-300"}`}
                >
                    {darkMode ? "☀️ Light" : "🌙 Dark"}
                </button>
            </div>

            {/* Hidden file input — triggered by button below */}
            <input type="file" accept=".pdf" ref={fileRef} onChange={uploadPDF} className="hidden" />

            {/* Upload button + filename display */}
            <div className="w-full max-w-2xl flex flex-wrap items-center gap-2 mb-4">
                <button
                    onClick={() => fileRef.current?.click()}
                    disabled={uploading}
                    className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
                >
                    {uploading ? "Uploading..." : "Upload PDF"}
                </button>
                {fileName && (
                    <span className="text-sm text-gray-600">
                        {fileName} {ready && <span className="text-green-600 font-medium">✓ Ready</span>}
                    </span>
                )}
                {error && (
                    <span className="text-sm text-red-600">
                        {error}
                    </span>
                )}
            </div>

            {/* Chat window */}
            <div className={`w-full max-w-2xl border rounded-xl flex flex-col transition-colors 
                    ${darkMode
                    ? "bg-gray-800 border-gray-700"
                    : "bg-white border-gray-200"}`}>

                {/* Scrollable message list */}
                <div className="flex-1 overflow-y-auto p-4 space-y-3">

                    {/* Empty state before PDF upload */}
                    {messages.length === 0 && (
                        <div className="text-center text-gray-400 text-sm mt-10">
                            Upload a PDF above to start chatting
                        </div>
                    )}

                    {/* Render all messages */}
                    {messages.map((msg, i) => (
                        <div
                            key={i}
                            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                        >
                            <div
                                className={`max-w-[80%] sm:max-w-xs lg:max-w-md px-4 py-2 rounded-2xl text-sm whitespace-pre-wrap
                                            ${msg.role === "user"
                                        ? "bg-blue-600 text-white rounded-br-sm"
                                        : darkMode
                                            ? "bg-gray-700 text-gray-100 rounded-bl-sm"
                                            : "bg-gray-100 text-gray-800 rounded-bl-sm"
                                    }`}
                            >
                                {msg.text}
                            </div>
                        </div>
                    ))}
                    {/* Typing indicator while waiting for response */}
                    {loading && (
                        <div className="flex justify-start">
                            <div className="bg-gray-100 text-gray-500 text-sm px-4 py-2 rounded-2xl">
                                Thinking...
                            </div>
                        </div>
                    )}

                    {/* Auto-scroll anchor */}
                    <div ref={bottomRef} />
                </div>

                {/* Input bar */}
                <div className={`border-t p-3 flex gap-2 ${darkMode ? "border-gray-700" : "border-gray-200"}`}>
                    <input
                        type="text"
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === "Enter" && sendMessage()}
                        placeholder={ready ? "Ask a question about the PDF..." : "Upload a PDF first..."}
                        disabled={!ready || loading}
                        className={`flex-1 text-sm border rounded-lg px-3 py-2 
                                    focus:outline-none focus:ring-2 focus:ring-blue-500
                                    disabled:opacity-50 transition-colors
                                    ${darkMode
                                ? "bg-gray-700 text-white border-gray-600 placeholder-gray-400"
                                : "bg-white text-gray-900 border-gray-300 placeholder-gray-400"}`}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={!ready || loading || !input.trim()}
                        className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
                    >
                        Send
                    </button>
                </div>
            </div>

        </div >
    );
}