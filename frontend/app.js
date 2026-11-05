/**
 * CodeAlpha AI FAQ Chatbot - React Application
 * Features:
 * - Real-time conversational interface with FastAPI backend
 * - Interactive predefined question chips (inspired by ResolveAI UI)
 * - Message history with timestamps and user/bot bubbles
 * - Confidence score badge and similarity indicator
 * - Fallback notification with human escalation link
 * - Dynamic confidence threshold slider for live tuning
 * - Knowledge base browser and test question explorer
 */

const { useState, useEffect, useRef } = React;

function App() {
  // Chat state
  const [messages, setMessages] = useState([
    {
      id: "welcome-1",
      sender: "bot",
      text: "👋 Hello! I am the **CodeAlpha AI Internship Assistant**.\n\nI can answer questions regarding your internship tasks, Python tech stack, GitHub project submission guidelines, certificates, and NLP pipeline details. How can I help you today?",
      timestamp: formatTime(new Date()),
      confidence: 1.0,
      isFallback: false,
      category: "Welcome",
      suggestedQuestions: [
        "What are the core tasks for the AI track?",
        "How do I submit my completed projects?",
        "When will I receive my certificate?",
        "How does the FAQ Chatbot NLP model work?"
      ],
    },
  ]);

  const [inputQuery, setInputQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [threshold, setThreshold] = useState(0.32);
  const [showSettings, setShowSettings] = useState(false);
  const [quickPrompts, setQuickPrompts] = useState([]);
  const [activeTab, setActiveTab] = useState("chat"); // 'chat' | 'faqs' | 'about'
  const [allFaqs, setAllFaqs] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [faqSearch, setFaqSearch] = useState("");

  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll on new message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Load knowledge base and starter prompts on mount
  useEffect(() => {
    fetchFaqs();
    fetchQuickPrompts();
  }, []);

  function formatTime(date) {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  async function fetchQuickPrompts() {
    try {
      const res = await fetch("/api/suggested-questions");
      if (res.ok) {
        const data = await res.json();
        setQuickPrompts(data.suggested_questions || []);
      }
    } catch (err) {
      console.warn("Could not load suggested questions:", err);
      setQuickPrompts([
        "What are the core tasks for the AI track?",
        "How do I submit my completed projects?",
        "When will I receive my certificate?",
        "Can I get a Letter of Recommendation?",
      ]);
    }
  }

  async function fetchFaqs() {
    try {
      const res = await fetch("/api/faqs");
      if (res.ok) {
        const data = await res.json();
        setAllFaqs(data.faqs || []);
        setCategories(["All", ...(data.categories || [])]);
        if (data.metadata?.default_threshold) {
          setThreshold(data.metadata.default_threshold);
        }
      }
    } catch (err) {
      console.warn("Could not fetch FAQs catalog:", err);
    }
  }

  async function handleSendMessage(queryText) {
    const textToSend = (typeof queryText === "string" ? queryText : inputQuery).trim();
    if (!textToSend || isLoading) return;

    // Append user message
    const userMsg = {
      id: "user-" + Date.now(),
      sender: "user",
      text: textToSend,
      timestamp: formatTime(new Date()),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: textToSend,
          threshold: parseFloat(threshold),
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const data = await response.json();

      const botMsg = {
        id: "bot-" + Date.now(),
        sender: "bot",
        text: data.reply,
        timestamp: formatTime(new Date()),
        confidence: data.confidence_score,
        isFallback: data.is_fallback,
        matchedQuestion: data.matched_question,
        matchedPattern: data.matched_pattern,
        category: data.category,
        faqId: data.faq_id,
        suggestedQuestions: data.suggested_questions || [],
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: "bot-err-" + Date.now(),
          sender: "bot",
          text: "⚠️ Connection error: Unable to reach the NLP matching server. Please ensure the backend is running.",
          timestamp: formatTime(new Date()),
          confidence: 0,
          isFallback: true,
        },
      ]);
    } finally {
      setIsLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }

  function handleClearChat() {
    if (window.confirm("Are you sure you want to clear your chat history?")) {
      setMessages([
        {
          id: "welcome-reset",
          sender: "bot",
          text: "Chat cleared. What can I help you with?",
          timestamp: formatTime(new Date()),
          confidence: 1.0,
          isFallback: false,
          suggestedQuestions: quickPrompts.slice(0, 3),
        },
      ]);
    }
  }

  function handleExportChat() {
    const transcript = messages
      .map(
        (m) =>
          `[${m.timestamp}] ${m.sender.toUpperCase()}: ${m.text}${
            m.confidence ? ` (Confidence: ${(m.confidence * 100).toFixed(1)}%)` : ""
          }`
      )
      .join("\n\n");

    const blob = new Blob([transcript], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `CodeAlpha_Chat_Transcript_${new Date().toISOString().slice(0, 10)}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  }

  const filteredFaqs = allFaqs.filter((faq) => {
    const matchesCategory = selectedCategory === "All" || faq.category === selectedCategory;
    const matchesSearch =
      faq.question.toLowerCase().includes(faqSearch.toLowerCase()) ||
      faq.answer.toLowerCase().includes(faqSearch.toLowerCase()) ||
      (faq.tags && faq.tags.some((t) => t.toLowerCase().includes(faqSearch.toLowerCase())));
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-900 text-slate-100 font-sans">
      {/* LEFT SIDEBAR (ResolveAI style) */}
      <aside className="hidden md:flex flex-col w-64 lg:w-72 bg-slate-950 border-r border-slate-800 p-4">
        {/* Brand */}
        <div className="flex items-center gap-3 px-2 py-3 border-b border-slate-800">
          <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-600/30">
            <i className="fas fa-robot text-lg"></i>
          </div>
          <div>
            <h1 className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
              CodeAlpha AI
              <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                NLP
              </span>
            </h1>
            <p className="text-xs text-slate-400">FAQ Intelligent Assistant</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="mt-5 space-y-1">
          <button
            onClick={() => setActiveTab("chat")}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === "chat"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            <i className="fas fa-comments w-4 text-center"></i>
            Live Assistant
          </button>

          <button
            onClick={() => setActiveTab("faqs")}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === "faqs"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            <i className="fas fa-book-open w-4 text-center"></i>
            FAQ Knowledge Base
            <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
              {allFaqs.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab("about")}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === "about"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            <i className="fas fa-microchip w-4 text-center"></i>
            NLP Model Specs
          </button>
        </nav>

        {/* Confidence Threshold Tuning Panel */}
        <div className="mt-6 p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs">
          <div className="flex items-center justify-between font-semibold text-slate-300 mb-2">
            <span>Confidence Threshold</span>
            <span className="px-2 py-0.5 rounded bg-indigo-950 text-indigo-400 font-mono border border-indigo-800/50">
              {(threshold * 100).toFixed(0)}%
            </span>
          </div>
          <input
            type="range"
            min="0.10"
            max="0.80"
            step="0.02"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="w-full accent-indigo-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
          />
          <p className="mt-2 text-[11px] text-slate-400 leading-relaxed">
            Cosine similarity cutoff. Queries scoring below threshold trigger fallback response.
          </p>
        </div>

        {/* Predefined Conversation Starters (From ResolveAI laptop image) */}
        <div className="mt-5 flex-1 overflow-y-auto">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 px-2 mb-2">
            Predefined Questions
          </h3>
          <div className="space-y-1.5">
            {quickPrompts.slice(0, 4).map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setActiveTab("chat");
                  handleSendMessage(prompt);
                }}
                className="w-full text-left px-3 py-2 rounded-lg text-xs text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-800/90 border border-slate-800/80 transition-colors line-clamp-2"
              >
                💬 {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Footer info */}
        <div className="pt-3 border-t border-slate-800/80 text-[11px] text-slate-500 flex items-center justify-between">
          <span>CodeAlpha AI Track</span>
          <span className="flex items-center gap-1.5 text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Online
          </span>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col h-full bg-slate-900 overflow-hidden relative">
        {/* Top Header */}
        <header className="h-16 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur px-4 md:px-6 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-md">
              <i className="fas fa-brain"></i>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-bold text-sm md:text-base text-white">ResolveAI Assistant</h2>
                <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  TF-IDF + Cosine Sim
                </span>
              </div>
              <p className="text-xs text-slate-400">Trained on CodeAlpha Internship Knowledge Base</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleExportChat}
              title="Export Chat Transcript"
              className="px-3 py-1.5 text-xs rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors flex items-center gap-1.5"
            >
              <i className="fas fa-download"></i>
              <span className="hidden sm:inline">Export</span>
            </button>
            <button
              onClick={handleClearChat}
              title="Clear Conversation"
              className="px-3 py-1.5 text-xs rounded-lg bg-slate-800 hover:bg-rose-950/40 text-slate-300 hover:text-rose-400 border border-transparent hover:border-rose-900/40 transition-colors flex items-center gap-1.5"
            >
              <i className="fas fa-trash-alt"></i>
              <span className="hidden sm:inline">Clear</span>
            </button>
          </div>
        </header>

        {/* TAB 1: LIVE CHAT */}
        {activeTab === "chat" && (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Messages Scroll Area */}
            <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-3 max-w-3xl message-bubble ${
                    msg.sender === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
                  }`}
                >
                  {/* Avatar */}
                  <div
                    className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-xs shadow ${
                      msg.sender === "user"
                        ? "bg-indigo-600 text-white"
                        : msg.isFallback
                        ? "bg-amber-600 text-white"
                        : "bg-slate-800 text-indigo-400 border border-slate-700"
                    }`}
                  >
                    {msg.sender === "user" ? (
                      <i className="fas fa-user"></i>
                    ) : (
                      <i className="fas fa-robot"></i>
                    )}
                  </div>

                  {/* Message Bubble Container */}
                  <div
                    className={`flex flex-col ${
                      msg.sender === "user" ? "items-end" : "items-start"
                    }`}
                  >
                    <div
                      className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
                        msg.sender === "user"
                          ? "bg-indigo-600 text-white rounded-tr-none"
                          : msg.isFallback
                          ? "bg-slate-800/95 border border-amber-500/30 text-slate-200 rounded-tl-none"
                          : "bg-slate-800/90 border border-slate-700/60 text-slate-200 rounded-tl-none"
                      }`}
                    >
                      {/* Formatted Text */}
                      <div className="whitespace-pre-wrap">{msg.text}</div>

                      {/* Confidence & Metadata Pill */}
                      {msg.sender === "bot" && (
                        <div className="mt-3 pt-2 border-t border-slate-700/60 flex flex-wrap items-center gap-2 text-[11px] text-slate-400">
                          {msg.category && (
                            <span className="px-2 py-0.5 rounded bg-slate-900/80 text-slate-300 font-medium border border-slate-700/50">
                              📂 {msg.category}
                            </span>
                          )}

                          {msg.confidence !== undefined && (
                            <span
                              className={`px-2 py-0.5 rounded font-mono font-semibold ${
                                msg.isFallback
                                  ? "bg-amber-950/60 text-amber-400 border border-amber-800/50"
                                  : msg.confidence >= 0.7
                                  ? "bg-emerald-950/60 text-emerald-400 border border-emerald-800/50"
                                  : "bg-indigo-950/60 text-indigo-400 border border-indigo-800/50"
                              }`}
                            >
                              {msg.isFallback ? "⚠️ Low Match: " : "🎯 Confidence: "}
                              {(msg.confidence * 100).toFixed(1)}%
                            </span>
                          )}

                          {msg.matchedPattern && (
                            <span className="hidden sm:inline text-slate-500 italic">
                              matched: "{msg.matchedPattern}"
                            </span>
                          )}
                        </div>
                      )}

                      {/* Suggested Questions Pill Options */}
                      {msg.suggestedQuestions && msg.suggestedQuestions.length > 0 && (
                        <div className="mt-3 pt-2.5 border-t border-slate-700/50">
                          <p className="text-[11px] font-semibold text-slate-400 mb-1.5 flex items-center gap-1">
                            <i className="fas fa-lightbulb text-amber-400"></i>
                            Suggested Questions:
                          </p>
                          <div className="flex flex-wrap gap-1.5">
                            {msg.suggestedQuestions.map((sug, i) => (
                              <button
                                key={i}
                                onClick={() => handleSendMessage(sug)}
                                className="text-[11px] px-2.5 py-1 rounded-md bg-slate-900/90 hover:bg-indigo-950/80 hover:text-indigo-300 hover:border-indigo-500/50 text-slate-300 border border-slate-700/80 transition-colors text-left"
                              >
                                {sug}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Timestamp */}
                    <span className="text-[10px] text-slate-500 mt-1 px-1">{msg.timestamp}</span>
                  </div>
                </div>
              ))}

              {/* Typing indicator */}
              {isLoading && (
                <div className="flex gap-3 max-w-md message-bubble mr-auto">
                  <div className="w-8 h-8 rounded-full bg-slate-800 text-indigo-400 border border-slate-700 flex items-center justify-center text-xs">
                    <i className="fas fa-robot"></i>
                  </div>
                  <div className="px-4 py-3 rounded-2xl rounded-tl-none bg-slate-800/90 border border-slate-700/60 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-indigo-400 typing-dot"></span>
                    <span className="w-2 h-2 rounded-full bg-indigo-400 typing-dot"></span>
                    <span className="w-2 h-2 rounded-full bg-indigo-400 typing-dot"></span>
                    <span className="ml-2 text-xs text-slate-400">Searching knowledge base...</span>
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>

            {/* Bottom Quick Chips Bar */}
            <div className="px-4 md:px-6 pt-2 pb-1 flex items-center gap-2 overflow-x-auto no-scrollbar">
              <span className="text-[11px] font-medium text-slate-400 flex items-center gap-1 flex-shrink-0">
                <i className="fas fa-bolt text-amber-400"></i> Quick:
              </span>
              {quickPrompts.slice(0, 5).map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSendMessage(q)}
                  className="flex-shrink-0 text-[11px] px-3 py-1 rounded-full bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700/70 transition-all hover:scale-105"
                >
                  {q}
                </button>
              ))}
            </div>

            {/* Input Bar */}
            <div className="p-4 md:p-6 pt-2 bg-slate-950/80 border-t border-slate-800/80">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSendMessage();
                }}
                className="flex items-center gap-2 max-w-4xl mx-auto bg-slate-900 border border-slate-700/80 rounded-2xl px-4 py-2.5 shadow-inner focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-500/20 transition-all"
              >
                <input
                  ref={inputRef}
                  type="text"
                  value={inputQuery}
                  onChange={(e) => setInputQuery(e.target.value)}
                  placeholder="Type your question (e.g. 'How do I submit my tasks?')..."
                  disabled={isLoading}
                  className="flex-1 bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
                />

                <button
                  type="submit"
                  disabled={isLoading || !inputQuery.trim()}
                  className="w-9 h-9 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:hover:bg-indigo-600 text-white flex items-center justify-center transition-all shadow-md shadow-indigo-600/30"
                >
                  <i className="fas fa-paper-plane text-xs"></i>
                </button>
              </form>
              <p className="text-[11px] text-center text-slate-500 mt-2">
                Confidence threshold set to {(threshold * 100).toFixed(0)}%. Try asking questions with different phrasing or typos!
              </p>
            </div>
          </div>
        )}

        {/* TAB 2: KNOWLEDGE BASE BROWSER */}
        {activeTab === "faqs" && (
          <div className="flex-1 flex flex-col p-4 md:p-6 overflow-hidden">
            {/* Filter and Search Bar */}
            <div className="flex flex-col sm:flex-row gap-3 items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto pb-1">
                {categories.map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                      selectedCategory === cat
                        ? "bg-indigo-600 text-white"
                        : "bg-slate-800 text-slate-400 hover:text-white"
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>

              <div className="w-full sm:w-64 relative">
                <i className="fas fa-search absolute left-3 top-2.5 text-xs text-slate-400"></i>
                <input
                  type="text"
                  value={faqSearch}
                  onChange={(e) => setFaqSearch(e.target.value)}
                  placeholder="Search questions or tags..."
                  className="w-full bg-slate-800 text-xs text-slate-100 pl-8 pr-3 py-2 rounded-lg border border-slate-700 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            {/* FAQs Grid */}
            <div className="flex-1 overflow-y-auto mt-4 space-y-3 pr-2">
              {filteredFaqs.map((faq) => (
                <div
                  key={faq.id}
                  className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 hover:border-indigo-500/50 transition-all group"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-950 text-indigo-400 font-medium border border-indigo-800/50">
                        {faq.category}
                      </span>
                      <span className="text-[10px] text-slate-500 font-mono">{faq.id}</span>
                    </div>

                    <button
                      onClick={() => {
                        setActiveTab("chat");
                        handleSendMessage(faq.question);
                      }}
                      className="text-xs px-2.5 py-1 rounded bg-slate-700 hover:bg-indigo-600 text-slate-300 hover:text-white transition-colors"
                    >
                      <i className="fas fa-paper-plane mr-1"></i> Ask Bot
                    </button>
                  </div>

                  <h3 className="font-semibold text-sm text-slate-100 mt-2 group-hover:text-indigo-300 transition-colors">
                    {faq.question}
                  </h3>

                  <p className="text-xs text-slate-300 mt-2 leading-relaxed bg-slate-900/60 p-3 rounded-lg border border-slate-800 whitespace-pre-wrap">
                    {faq.answer}
                  </p>

                  {/* Patterns */}
                  {faq.patterns && faq.patterns.length > 0 && (
                    <div className="mt-3">
                      <span className="text-[10px] uppercase font-semibold text-slate-500">
                        Recognized variations:
                      </span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {faq.patterns.map((pat, i) => (
                          <span
                            key={i}
                            onClick={() => {
                              setActiveTab("chat");
                              handleSendMessage(pat);
                            }}
                            className="text-[11px] px-2 py-0.5 rounded bg-slate-900 text-slate-400 hover:text-indigo-300 hover:border-indigo-500/40 border border-slate-800 cursor-pointer"
                          >
                            "{pat}"
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 3: NLP MODEL SPECIFICATIONS */}
        {activeTab === "about" && (
          <div className="flex-1 p-6 overflow-y-auto max-w-4xl space-y-6">
            <div className="p-6 rounded-2xl bg-slate-800/80 border border-slate-700">
              <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                <i className="fas fa-cogs text-indigo-400"></i>
                CodeAlpha FAQ Chatbot Architecture
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed">
                This project implements a complete Natural Language Processing (NLP) pipeline designed for FAQ intent recognition and retrieval.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <h4 className="font-semibold text-sm text-indigo-400 mb-2">1. Text Preprocessing (NLTK)</h4>
                  <ul className="text-xs text-slate-300 space-y-1.5 list-disc list-inside">
                    <li>Case normalization and punctuation removal</li>
                    <li>Typo auto-correction for student queries</li>
                    <li>Word tokenization via NLTK word_tokenize</li>
                    <li>Stopword removal with interrogative preservation</li>
                    <li>WordNet Lemmatization for verb/noun roots</li>
                  </ul>
                </div>

                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <h4 className="font-semibold text-sm text-indigo-400 mb-2">2. Vectorization & Matching (scikit-learn)</h4>
                  <ul className="text-xs text-slate-300 space-y-1.5 list-disc list-inside">
                    <li>TF-IDF Vectorizer with n-grams (1, 2)</li>
                    <li>Sublinear TF scaling for frequency smoothing</li>
                    <li>Cosine Similarity distance metric</li>
                    <li>Tunable confidence cutoff threshold ({threshold})</li>
                    <li>Intelligent fallback with top-k suggested questions</li>
                  </ul>
                </div>
              </div>

              <div className="mt-6 p-4 rounded-xl bg-indigo-950/40 border border-indigo-900/50">
                <h4 className="font-semibold text-sm text-indigo-300 mb-2">Spelling & Typo Tolerance</h4>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Try typing queries with intentional variations such as:
                  <code className="text-indigo-300 bg-slate-900 px-1.5 py-0.5 rounded mx-1">
                    "When do i get my certifcate?"
                  </code>
                  or
                  <code className="text-indigo-300 bg-slate-900 px-1.5 py-0.5 rounded mx-1">
                    "Can i get deadline extention for submited projcet?"
                  </code>
                  The pipeline normalizes these variations and maps them to the accurate FAQ response!
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

// Mount the React Application
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
