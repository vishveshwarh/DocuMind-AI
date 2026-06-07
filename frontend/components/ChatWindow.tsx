"use client";
import { useState, useRef, useEffect } from "react";

type Message = {
    role: "user" | "bot";
    text: string;
};

export default function ChatWindow() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [ready, setReady] = useState(false);
    const [fileName, setFileName] = useState("");
    const fileRef = useRef<HTMLInputElement>(null);
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    const uploadPDF = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setUploading(true);
        setFileName(file.name);

        // FormData is the standard way to send files over HTTP
        const form = new FormData();
        form.append("file", file);

        try {
            const res = await fetch(`${API_URL}/upload`, {
                method: "POST",
                body: form,
            });
            const data = await res.json();

            // Show backend's success message as first bot message
            setMessages([{ role: "bot", text: `✅ ${data.message}` }]);
            setReady(true);
        } catch {
            setMessages([{ role: "bot", text: "❌ Upload failed. Is the backend running?" }]);
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
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question }),
            });
            const data = await res.json();
            setMessages(prev => [...prev, { role: "bot", text: data.answer }]);
        } catch {
            setMessages(prev => [...prev, { role: "bot", text: "❌ Error. Is the backend running?" }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center py-6 px-3 sm:py-10 sm:px-4">

            {/* App header */}
            <div className="w-full max-w-2xl mb-4 sm:mb-6">
                <h1 className="text-2xl font-semibold text-gray-800">RAG Chatbot</h1>
                <p className="text-sm text-gray-500 mt-1">Upload a PDF and ask questions about it</p>
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
            </div>

            {/* Chat window */}
            <div className="w-full max-w-2xl bg-white border border-gray-200 rounded-xl flex flex-col" style={{ height: "65vh" }}>

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
                        <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                            <div className={`max-w-[80%] sm:max-w-xs lg:max-w-md px-4 py-2 rounded-2xl text-sm ${msg.role === "user"
                                    ? "bg-blue-600 text-white rounded-br-sm"
                                    : "bg-gray-100 text-gray-800 rounded-bl-sm"
                                }`}>
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
                <div className="border-t border-gray-200 p-3 flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === "Enter" && sendMessage()}
                        placeholder={ready ? "Ask a question about the PDF..." : "Upload a PDF first..."}
                        disabled={!ready || loading}
                        className="flex-1 text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-400"
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

        </div>
    );
}