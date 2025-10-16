import React from "react";

interface WeekStats {
  time_saved_min: number;
  cost_avoided_usd: number;
  success_rate_pct: number;
  prompts_created: number;
}

interface AllTimeStats {
  time_saved_hr: number;
  cost_avoided_usd: number;
  prompts_created: number;
  in_prod: number;
}

interface ImpactDashboardProps {
  week: WeekStats;
  all_time: AllTimeStats;
}

export default function ImpactDashboard({ week, all_time }: ImpactDashboardProps) {
  const handleShare = () => {
    const text = `I just optimized my AI prompts with Prompt Gauge:

⏱️  Time saved: ${all_time.time_saved_hr} hours
💰 Cost avoided: $${all_time.cost_avoided_usd}
🎯 Success rate: ${week.success_rate_pct}%
📝 Prompts created: ${all_time.prompts_created}

It's like Grammarly for ChatGPT prompts.

Try it free: promptgauge.com

#AI #ChatGPT #ProductivityTools`;

    navigator.clipboard.writeText(text);
    alert("📋 LinkedIn post copied to clipboard! Paste it on LinkedIn to share your success.");
  };

  return (
    <div style={{ 
      background: "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
      padding: 32, 
      borderRadius: 16,
      color: "white",
      marginTop: 24
    }}>
      <h2 style={{ textAlign: "center", margin: "0 0 8px 0", fontSize: 32, fontWeight: 700 }}>
        💰 Your Personal Impact
      </h2>
      <p style={{ textAlign: "center", margin: "0 0 32px 0", fontSize: 16, opacity: 0.9 }}>
        See how much time and money you've saved
      </p>
      
      <div style={{ 
        display: "grid", 
        gridTemplateColumns: "1fr 1fr", 
        gap: 24
      }}>
        {/* This Week */}
        <div style={{ 
          background: "rgba(255,255,255,0.95)", 
          padding: 24, 
          borderRadius: 12,
          color: "#333"
        }}>
          <h3 style={{ margin: "0 0 20px 0", fontSize: 20, fontWeight: 700, color: "#11998e" }}>
            📅 This Week
          </h3>
          
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 14, color: "#666", marginBottom: 4 }}>⏱️ Time Saved</div>
            <div style={{ fontSize: 32, fontWeight: 700, color: "#11998e" }}>
              {week.time_saved_min} <span style={{ fontSize: 16 }}>minutes</span>
            </div>
            <div style={{ fontSize: 12, color: "#999" }}>(vs manual testing)</div>
          </div>
          
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 14, color: "#666", marginBottom: 4 }}>💵 Cost Avoided</div>
            <div style={{ fontSize: 32, fontWeight: 700, color: "#11998e" }}>
              ${week.cost_avoided_usd.toFixed(2)}
            </div>
            <div style={{ fontSize: 12, color: "#999" }}>(wasted API calls)</div>
          </div>
          
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 14, color: "#666", marginBottom: 4 }}>🎯 Success Rate</div>
            <div style={{ fontSize: 32, fontWeight: 700, color: "#11998e" }}>
              {week.success_rate_pct}%
            </div>
            <div style={{ fontSize: 12, color: "#999" }}>(vs 67% unoptimized)</div>
          </div>
          
          <div>
            <div style={{ fontSize: 14, color: "#666", marginBottom: 4 }}>📝 Prompts Created</div>
            <div style={{ fontSize: 32, fontWeight: 700, color: "#11998e" }}>
              {week.prompts_created}
            </div>
          </div>
        </div>
        
        {/* All Time */}
        <div style={{ 
          background: "rgba(255,255,255,0.95)", 
          padding: 24, 
          borderRadius: 12,
          color: "#333"
        }}>
          <h3 style={{ margin: "0 0 20px 0", fontSize: 20, fontWeight: 700, color: "#11998e" }}>
            🏆 All Time
          </h3>
          
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 14, color: "#666", marginBottom: 4 }}>⏱️ Time Saved</div>
            <div style={{ fontSize: 32, fontWeight: 700, color: "#11998e" }}>
              {all_time.time_saved_hr} <span style={{ fontSize: 16 }}>hours</span>
            </div>
            <div style={{ fontSize: 12, color: "#999" }}>({all_time.in_prod} prompts × 15min ea)</div>
          </div>
          
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 14, color: "#666", marginBottom: 4 }}>💵 Cost Avoided</div>
            <div style={{ fontSize: 32, fontWeight: 700, color: "#11998e" }}>
              ${all_time.cost_avoided_usd.toFixed(2)}
            </div>
            <div style={{ fontSize: 12, color: "#999" }}>(failed attempts)</div>
          </div>
          
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 14, color: "#666", marginBottom: 4 }}>📝 Prompts Created</div>
            <div style={{ fontSize: 32, fontWeight: 700, color: "#11998e" }}>
              {all_time.prompts_created}
            </div>
          </div>
          
          <div>
            <div style={{ fontSize: 14, color: "#666", marginBottom: 4 }}>✅ Production Quality</div>
            <div style={{ fontSize: 32, fontWeight: 700, color: "#11998e" }}>
              {all_time.in_prod}
            </div>
          </div>
        </div>
      </div>
      
      {/* Share Button */}
      <div style={{ textAlign: "center", marginTop: 24 }}>
        <button
          onClick={handleShare}
          style={{
            padding: "14px 32px",
            fontSize: 18,
            fontWeight: 700,
            background: "#ffffff",
            color: "#11998e",
            border: "none",
            borderRadius: 10,
            cursor: "pointer",
            boxShadow: "0 4px 12px rgba(0,0,0,0.15)"
          }}
        >
          📊 Share My Stats on LinkedIn
        </button>
      </div>
    </div>
  );
}

