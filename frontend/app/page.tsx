"use client";

import { useState, useEffect } from "react";
import BeforeAfter from "../components/BeforeAfter";
import ImpactDashboard from "../components/ImpactDashboard";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

// Style mapping for user-friendly names
const STYLE_INFO = {
  directive: {
    name: "Quick & Direct",
    description: "Give AI clear, step-by-step instructions",
    icon: "⚡",
    speed: "Fast",
    cost: "Cheap",
    bestFor: "Works for 80% of tasks"
  },
  few_shot: {
    name: "With Examples",
    description: "Show AI 2-3 examples of what you want",
    icon: "📚",
    speed: "Medium",
    cost: "Medium",
    bestFor: "Great for formatting tasks"
  },
  schema_json: {
    name: "Structured Output",
    description: "Get results in a specific format (like Excel/JSON)",
    icon: "📊",
    speed: "Fast",
    cost: "Cheap",
    bestFor: "Perfect for organizing data"
  },
  planner_executor: {
    name: "Step-by-Step",
    description: "Break big tasks into smaller steps",
    icon: "🔄",
    speed: "Slower",
    cost: "Higher",
    bestFor: "For multi-step work"
  },
  rubric_scored: {
    name: "Quality Checked",
    description: "AI double-checks its own work",
    icon: "✅",
    speed: "Slower",
    cost: "Higher",
    bestFor: "For important outputs"
  }
};

export default function Home() {
  const [goal, setGoal] = useState("");
  const [useLLM, setUseLLM] = useState(false);
  const [explainRes, setExplainRes] = useState<any>(null);
  const [genStyle, setGenStyle] = useState("directive");
  const [genRes, setGenRes] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedPlatform, setSelectedPlatform] = useState("chatgpt");
  const [compareRes, setCompareRes] = useState<any>(null);
  const [existingPrompt, setExistingPrompt] = useState("");
  const [stats, setStats] = useState<any>(null);

  async function doExplain() {
    setLoading(true);
    setError("");
    try {
      const headers: any = { "Content-Type": "application/json" };
      if (useLLM) {
        headers["x-use-llm"] = "true";
      }
      
      const r = await fetch(`${API}/explain`, {
        method: "POST",
        headers,
        body: JSON.stringify({ goal }),
      });
      const j = await r.json();
      setExplainRes(j);
    } catch (e) {
      setError("Oops! We couldn't check your idea right now. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function doGenerate() {
    setLoading(true);
    setError("");
    try {
      const r = await fetch(`${API}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal, style: genStyle }),
      });
      const j = await r.json();
      setGenRes(j);
      fetchHistory();
      fetchStats();
    } catch (e) {
      setError("Oops! We couldn't create your AI instructions. Don't worry, your idea is saved. Try again in a moment.");
    } finally {
      setLoading(false);
    }
  }

  async function fetchHistory() {
    try {
      const r = await fetch(`${API}/runs?limit=5`);
      const j = await r.json();
      setHistory(j);
    } catch (e) {
      console.error("Failed to fetch history:", e);
    }
  }

  async function fetchStats() {
    try {
      const r = await fetch(`${API}/stats/me`);
      const j = await r.json();
      setStats(j);
    } catch (e) {
      console.error("Failed to fetch stats:", e);
    }
  }

  async function doCompare() {
    if (!existingPrompt.trim()) {
      setError("Please paste a prompt to analyze");
      return;
    }
    
    setLoading(true);
    setError("");
    try {
      const r = await fetch(`${API}/compare`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: existingPrompt }),
      });
      const j = await r.json();
      setCompareRes(j);
      fetchStats();
    } catch (e) {
      setError("Oops! We couldn't analyze your prompt. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleShareComparison() {
    // Image export is now handled in BeforeAfter component
    console.log("Share functionality integrated in BeforeAfter component");
  }

  useEffect(() => {
    fetchHistory();
    fetchStats();
  }, []);

  const renderStars = (score: number) => {
    const filled = "⭐";
    const empty = "☆";
    return filled.repeat(score) + empty.repeat(10 - score);
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const then = new Date(timestamp);
    const seconds = Math.floor((now.getTime() - then.getTime()) / 1000);
    
    if (seconds < 60) return "just now";
    if (seconds < 3600) return `${Math.floor(seconds / 60)} mins ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    return `${Math.floor(seconds / 86400)} days ago`;
  };

  return (
    <main style={{ maxWidth: 1200, margin: "40px auto", padding: 20, fontFamily: "system-ui, -apple-system, sans-serif" }}>
      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: 40 }}>
        <h1 style={{ fontSize: 48, margin: "0 0 16px 0", fontWeight: 700 }}>
          🎯 AI Prompt Builder
        </h1>
        <p style={{ fontSize: 20, color: "#666", margin: 0 }}>
          Turn your idea into ready-to-use AI instructions
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div style={{ 
          padding: 16, 
          background: "#fff3cd", 
          border: "1px solid #ffc107", 
          borderRadius: 8, 
          marginBottom: 24 
        }}>
          <strong>😕 {error}</strong>
        </div>
      )}

      {/* PROMPT DOCTOR: Analyze Existing Prompt */}
      <div style={{ background: "#fff9e6", padding: 24, borderRadius: 12, marginBottom: 32, border: "2px solid #ffc107" }}>
        <h2 style={{ margin: "0 0 8px 0", fontSize: 24 }}>
          🩺 AI Prompt Doctor
        </h2>
        <p style={{ color: "#666", marginBottom: 16 }}>
          Already have a prompt? Paste it here and we'll find and fix problems you didn't know existed.
        </p>
        
        <textarea
          value={existingPrompt}
          onChange={(e) => setExistingPrompt(e.target.value)}
          rows={4}
          style={{ 
            width: "100%", 
            fontFamily: "monospace", 
            padding: 16,
            fontSize: 14,
            border: "2px solid #ffc107",
            borderRadius: 8,
            resize: "vertical"
          }}
          placeholder='Paste your existing prompt here. Example: "Summarize this meeting" or "Help me write an email"'
        />
        
        <button 
          onClick={doCompare} 
          disabled={loading || !existingPrompt}
          style={{
            marginTop: 12,
            padding: "12px 24px",
            fontSize: 16,
            fontWeight: 600,
            background: "#ffc107",
            color: "#000",
            border: "none",
            borderRadius: 8,
            cursor: loading || !existingPrompt ? "not-allowed" : "pointer",
            opacity: loading || !existingPrompt ? 0.6 : 1
          }}
        >
          🩺 Diagnose My Prompt
        </button>
      </div>

      {/* Before/After Comparison Results */}
      {compareRes && (
        <BeforeAfter 
          before={compareRes.before}
          after={compareRes.after}
          improvement_pct={compareRes.improvement_pct}
          onShare={handleShareComparison}
        />
      )}

      <div style={{ textAlign: "center", margin: "40px 0", color: "#999" }}>
        ━━━━━━  OR  ━━━━━━
      </div>

      {/* Main Input */}
      <div style={{ background: "#f8f9fa", padding: 24, borderRadius: 12, marginBottom: 24 }}>
        <label style={{ display: "block", fontSize: 18, fontWeight: 600, marginBottom: 12 }}>
          💡 What do you want AI to do?
        </label>
        <textarea
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          rows={6}
          style={{ 
            width: "100%", 
            fontFamily: "inherit", 
            padding: 16,
            fontSize: 16,
            border: "2px solid #dee2e6",
            borderRadius: 8,
            resize: "vertical"
          }}
          placeholder='Example: "Help me summarize meeting notes and pull out action items with who should do what and by when"'
        />
        
        <div style={{ display: "flex", gap: 12, marginTop: 16, alignItems: "center", flexWrap: "wrap" }}>
          <button 
            onClick={doExplain} 
            disabled={loading || !goal}
            style={{
              padding: "12px 24px",
              fontSize: 16,
              fontWeight: 600,
              background: "#0d6efd",
              color: "white",
              border: "none",
              borderRadius: 8,
              cursor: loading || !goal ? "not-allowed" : "pointer",
              opacity: loading || !goal ? 0.6 : 1
            }}
          >
            ✨ Check My Idea
          </button>
          
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 14, color: "#666" }}>
            <input 
              type="checkbox" 
              checked={useLLM} 
              onChange={(e) => setUseLLM(e.target.checked)}
            />
            Use AI to refine my idea (slower but smarter)
          </label>
        </div>
      </div>

      {/* Explain Results */}
      {explainRes && (
        <div style={{ 
          background: "#d4edda", 
          padding: 24, 
          borderRadius: 12, 
          marginBottom: 24,
          border: "2px solid #28a745"
        }}>
          <h2 style={{ margin: "0 0 16px 0", fontSize: 24 }}>
            ✅ Your Idea Health Check
          </h2>
          
          <div style={{ marginBottom: 16 }}>
            <strong>Clarity:</strong> {renderStars(explainRes.readiness_score)} ({explainRes.readiness_score}/10 - {explainRes.readiness_score >= 8 ? "Great!" : explainRes.readiness_score >= 6 ? "Good" : "Needs work"})
          </div>

          <div style={{ background: "white", padding: 16, borderRadius: 8, marginBottom: 12 }}>
            <p><strong>What you want:</strong> {explainRes.intent}</p>
            <p><strong>What you'll provide:</strong> {explainRes.inputs?.join(", ")}</p>
            <p><strong>What you'll get:</strong> {explainRes.outputs?.join(", ")}</p>
            {explainRes.constraints?.length > 0 && (
              <p><strong>Special requirements:</strong> {explainRes.constraints.join(", ")}</p>
            )}
          </div>

          {explainRes.missing?.length > 0 && (
            <div style={{ background: "#fff3cd", padding: 16, borderRadius: 8 }}>
              <strong>💡 To make this even better:</strong>
              <ul style={{ margin: "8px 0 0 0", paddingLeft: 20 }}>
                {explainRes.missing.map((m: string, i: number) => (
                  <li key={i}>{m}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Style Picker */}
      <div style={{ background: "#f8f9fa", padding: 24, borderRadius: 12, marginBottom: 24 }}>
        <h2 style={{ margin: "0 0 16px 0", fontSize: 24 }}>
          📋 Choose Your Template
        </h2>
        <p style={{ color: "#666", marginBottom: 20 }}>
          Which approach works best for your task?
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
          {Object.entries(STYLE_INFO).map(([key, info]) => (
            <label
              key={key}
              style={{
                display: "block",
                padding: 16,
                background: genStyle === key ? "#e7f3ff" : "white",
                border: `2px solid ${genStyle === key ? "#0d6efd" : "#dee2e6"}`,
                borderRadius: 8,
                cursor: "pointer",
                transition: "all 0.2s"
              }}
            >
              <input
                type="radio"
                name="style"
                value={key}
                checked={genStyle === key}
                onChange={(e) => setGenStyle(e.target.value)}
                style={{ marginRight: 8 }}
              />
              <span style={{ fontSize: 20 }}>{info.icon}</span>{" "}
              <strong>{info.name}</strong>
              <p style={{ margin: "8px 0 0 0", fontSize: 14, color: "#666" }}>
                {info.description}
              </p>
              <div style={{ fontSize: 12, color: "#999", marginTop: 8 }}>
                ⏱️ {info.speed} • 💰 {info.cost} • ✅ {info.bestFor}
              </div>
            </label>
          ))}
        </div>

        <div style={{ marginTop: 20, textAlign: "center" }}>
          <button 
            onClick={doGenerate} 
            disabled={loading || !goal}
            style={{
              padding: "14px 32px",
              fontSize: 18,
              fontWeight: 700,
              background: "#28a745",
              color: "white",
              border: "none",
              borderRadius: 8,
              cursor: loading || !goal ? "not-allowed" : "pointer",
              opacity: loading || !goal ? 0.6 : 1
            }}
          >
            🚀 Make It Ready to Use
          </button>
        </div>
        
        <p style={{ textAlign: "center", fontSize: 14, color: "#666", marginTop: 12 }}>
          Not sure which to pick? Try "Quick & Direct" first →
        </p>
      </div>

      {/* Generated Output */}
      {genRes && (
        <div style={{ 
          background: "#e7f3ff", 
          padding: 24, 
          borderRadius: 12, 
          marginBottom: 24,
          border: "2px solid #0d6efd"
        }}>
          <h2 style={{ margin: "0 0 16px 0", fontSize: 24 }}>
            ✅ Your AI Instructions Are Ready!
          </h2>
          
          <div style={{ marginBottom: 16 }}>
            <strong>Template:</strong> {STYLE_INFO[genRes.style as keyof typeof STYLE_INFO]?.name || genRes.style}
          </div>

          {genRes.is_dual_prompt ? (
            <>
              <div style={{ background: "white", padding: 16, borderRadius: 8, marginBottom: 16 }}>
                <h3 style={{ margin: "0 0 12px 0" }}>📝 Planning Instructions:</h3>
                <pre style={{ whiteSpace: "pre-wrap", fontFamily: "monospace", fontSize: 14, margin: 0 }}>
                  {genRes.planner_prompt}
                </pre>
              </div>
              <div style={{ background: "white", padding: 16, borderRadius: 8, marginBottom: 16 }}>
                <h3 style={{ margin: "0 0 12px 0" }}>📝 Execution Instructions:</h3>
                <pre style={{ whiteSpace: "pre-wrap", fontFamily: "monospace", fontSize: 14, margin: 0 }}>
                  {genRes.executor_prompt}
                </pre>
              </div>
            </>
          ) : (
            <div style={{ background: "white", padding: 16, borderRadius: 8, marginBottom: 16 }}>
              <h3 style={{ margin: "0 0 12px 0" }}>📝 Instructions for AI:</h3>
              <pre style={{ whiteSpace: "pre-wrap", fontFamily: "monospace", fontSize: 14, margin: 0 }}>
                {genRes.prompt_body}
              </pre>
            </div>
          )}

          {/* Platform Guide */}
          <div style={{ background: "white", padding: 16, borderRadius: 8, marginBottom: 16 }}>
            <h3 style={{ margin: "0 0 12px 0" }}>🔧 How to Use This</h3>
            <p style={{ marginBottom: 12 }}>Choose your platform:</p>
            
            <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
              <button
                onClick={() => setSelectedPlatform("chatgpt")}
                style={{
                  padding: "8px 16px",
                  background: selectedPlatform === "chatgpt" ? "#0d6efd" : "#e9ecef",
                  color: selectedPlatform === "chatgpt" ? "white" : "black",
                  border: "none",
                  borderRadius: 6,
                  cursor: "pointer",
                  fontWeight: 600
                }}
              >
                ChatGPT
              </button>
              <button
                onClick={() => setSelectedPlatform("claude")}
                style={{
                  padding: "8px 16px",
                  background: selectedPlatform === "claude" ? "#0d6efd" : "#e9ecef",
                  color: selectedPlatform === "claude" ? "white" : "black",
                  border: "none",
                  borderRadius: 6,
                  cursor: "pointer",
                  fontWeight: 600
                }}
              >
                Claude
              </button>
              <button
                onClick={() => setSelectedPlatform("api")}
                style={{
                  padding: "8px 16px",
                  background: selectedPlatform === "api" ? "#0d6efd" : "#e9ecef",
                  color: selectedPlatform === "api" ? "white" : "black",
                  border: "none",
                  borderRadius: 6,
                  cursor: "pointer",
                  fontWeight: 600
                }}
              >
                Custom API
              </button>
            </div>

            {selectedPlatform === "chatgpt" && (
              <div style={{ padding: 12, background: "#f8f9fa", borderRadius: 6 }}>
                <ol style={{ margin: 0, paddingLeft: 20 }}>
                  <li>Copy the instructions above</li>
                  <li>Go to <a href="https://chat.openai.com" target="_blank" rel="noopener">chat.openai.com</a></li>
                  <li>Paste the instructions and add your content</li>
                  <li>Hit send!</li>
                </ol>
              </div>
            )}

            {selectedPlatform === "claude" && (
              <div style={{ padding: 12, background: "#f8f9fa", borderRadius: 6 }}>
                <ol style={{ margin: 0, paddingLeft: 20 }}>
                  <li>Copy the instructions above</li>
                  <li>Go to <a href="https://claude.ai" target="_blank" rel="noopener">claude.ai</a></li>
                  <li>Paste the instructions and add your content</li>
                  <li>Hit send!</li>
                </ol>
              </div>
            )}

            {selectedPlatform === "api" && !genRes.is_dual_prompt && (
              <div>
                <details>
                  <summary style={{ cursor: "pointer", fontWeight: 600, marginBottom: 8 }}>
                    Show Python Code
                  </summary>
                  <pre style={{ whiteSpace: "pre-wrap", fontFamily: "monospace", fontSize: 12, background: "#f8f9fa", padding: 12, borderRadius: 6, overflow: "auto" }}>
                    {genRes.language_variants?.python}
                  </pre>
                </details>
                <details>
                  <summary style={{ cursor: "pointer", fontWeight: 600, margin: "8px 0" }}>
                    Show JavaScript Code
                  </summary>
                  <pre style={{ whiteSpace: "pre-wrap", fontFamily: "monospace", fontSize: 12, background: "#f8f9fa", padding: 12, borderRadius: 6, overflow: "auto" }}>
                    {genRes.language_variants?.javascript}
                  </pre>
                </details>
                <details>
                  <summary style={{ cursor: "pointer", fontWeight: 600, marginTop: 8 }}>
                    Show cURL Command
                  </summary>
                  <pre style={{ whiteSpace: "pre-wrap", fontFamily: "monospace", fontSize: 12, background: "#f8f9fa", padding: 12, borderRadius: 6, overflow: "auto" }}>
                    {genRes.language_variants?.curl}
                  </pre>
                </details>
              </div>
            )}
          </div>

          <button
            onClick={() => {
              navigator.clipboard.writeText(genRes.prompt_body);
              alert("📋 Copied to clipboard!");
            }}
            style={{
              padding: "12px 24px",
              fontSize: 16,
              fontWeight: 600,
              background: "#28a745",
              color: "white",
              border: "none",
              borderRadius: 8,
              cursor: "pointer",
              width: "100%"
            }}
          >
            📋 Copy Instructions to Clipboard
          </button>
        </div>
      )}

      {/* History */}
      {history.length > 0 && (
        <div style={{ background: "#f8f9fa", padding: 24, borderRadius: 12 }}>
          <h2 style={{ margin: "0 0 16px 0", fontSize: 24 }}>
            📚 Your Recent Projects
          </h2>
          <div style={{ overflow: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ borderBottom: "2px solid #dee2e6" }}>
                  <th style={{ textAlign: "left", padding: 12, fontWeight: 600 }}>Template</th>
                  <th style={{ textAlign: "left", padding: 12, fontWeight: 600 }}>When</th>
                </tr>
              </thead>
              <tbody>
                {history.map((run) => (
                  <tr key={run.id} style={{ borderBottom: "1px solid #dee2e6" }}>
                    <td style={{ padding: 12 }}>
                      {STYLE_INFO[run.style as keyof typeof STYLE_INFO]?.icon || "📝"}{" "}
                      {STYLE_INFO[run.style as keyof typeof STYLE_INFO]?.name || run.style}
                    </td>
                    <td style={{ padding: 12, color: "#666" }}>
                      {getTimeAgo(run.started_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Impact Dashboard */}
      {stats && (
        <ImpactDashboard 
          week={stats.week}
          all_time={stats.all_time}
        />
      )}
    </main>
  );
}
