import React, { useRef } from "react";

interface PromptData {
  prompt: string;
  score: number;
  problems: string[];
  expected_quality_pct: number;
  fixes?: string[];
}

interface BeforeAfterProps {
  before: PromptData;
  after: PromptData;
  improvement_pct: number;
  onShare?: () => void;
}

const renderStars = (score: number) => {
  const filled = "⭐";
  const empty = "☆";
  return filled.repeat(score) + empty.repeat(10 - score);
};

export default function BeforeAfter({ before, after, improvement_pct, onShare }: BeforeAfterProps) {
  const cardRef = useRef<HTMLDivElement>(null);

  const handleShareImage = async () => {
    if (!cardRef.current) return;
    
    try {
      // Dynamically import html2canvas
      const html2canvas = (await import("html2canvas")).default;
      
      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: "#667eea",
        scale: 2, // Higher resolution
        logging: false
      });
      
      // Convert to blob
      canvas.toBlob((blob) => {
        if (blob) {
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `prompt-transformation-${improvement_pct}pct.png`;
          a.click();
          URL.revokeObjectURL(url);
          
          alert("📸 Image downloaded! Share it on LinkedIn to show your transformation.");
        }
      });
      
    } catch (error) {
      console.error("Failed to export image:", error);
      alert("📸 Couldn't export image. Try taking a screenshot instead!");
    }
  };

  return (
    <div ref={cardRef} id="before-after-comparison" style={{ 
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      padding: 32, 
      borderRadius: 16, 
      marginTop: 24,
      color: "white"
    }}>
      <h2 style={{ textAlign: "center", margin: "0 0 32px 0", fontSize: 32, fontWeight: 700 }}>
        🔄 Prompt Transformation
      </h2>
      
      <div style={{ 
        display: "grid", 
        gridTemplateColumns: "1fr auto 1fr", 
        gap: 24,
        alignItems: "start"
      }}>
        {/* BEFORE Column */}
        <div style={{ 
          background: "rgba(255,255,255,0.95)", 
          padding: 20, 
          borderRadius: 12,
          color: "#333"
        }}>
          <h3 style={{ margin: "0 0 16px 0", color: "#dc3545", fontSize: 20 }}>
            ❌ BEFORE
          </h3>
          
          <div style={{ 
            background: "#f8f9fa", 
            padding: 16, 
            borderRadius: 8, 
            marginBottom: 16,
            minHeight: 100
          }}>
            <pre style={{ 
              whiteSpace: "pre-wrap", 
              fontFamily: "monospace", 
              fontSize: 14,
              margin: 0,
              color: "#666"
            }}>
              {before.prompt}
            </pre>
          </div>
          
          <div style={{ marginBottom: 12 }}>
            <strong>Clarity:</strong> {renderStars(before.score)}
            <div style={{ fontSize: 24, fontWeight: 700, color: "#dc3545", marginTop: 4 }}>
              {before.score}/10
            </div>
          </div>
          
          <div style={{ marginBottom: 12 }}>
            <strong style={{ color: "#dc3545" }}>
              {before.problems.length} problems found:
            </strong>
            <ul style={{ 
              margin: "8px 0 0 0", 
              paddingLeft: 20, 
              fontSize: 13,
              lineHeight: 1.6
            }}>
              {before.problems.slice(0, 6).map((problem, i) => (
                <li key={i}>{problem}</li>
              ))}
            </ul>
          </div>
          
          <div style={{ 
            background: "#fff3cd", 
            padding: 12, 
            borderRadius: 6,
            color: "#856404"
          }}>
            <strong>Expected Quality:</strong> {before.expected_quality_pct}%
          </div>
        </div>
        
        {/* CENTER Arrow + Badge */}
        <div style={{ 
          display: "flex", 
          flexDirection: "column", 
          alignItems: "center",
          justifyContent: "center",
          minWidth: 120
        }}>
          <div style={{ 
            fontSize: 48, 
            margin: "20px 0"
          }}>
            →
          </div>
          
          <div style={{ 
            background: "#ffc107",
            color: "#000",
            padding: "12px 20px",
            borderRadius: 12,
            fontWeight: 700,
            textAlign: "center",
            boxShadow: "0 4px 12px rgba(0,0,0,0.2)"
          }}>
            <div style={{ fontSize: 32 }}>🚀</div>
            <div style={{ fontSize: 24 }}>{improvement_pct}%</div>
            <div style={{ fontSize: 12 }}>improvement</div>
          </div>
        </div>
        
        {/* AFTER Column */}
        <div style={{ 
          background: "rgba(255,255,255,0.95)", 
          padding: 20, 
          borderRadius: 12,
          color: "#333"
        }}>
          <h3 style={{ margin: "0 0 16px 0", color: "#28a745", fontSize: 20 }}>
            ✅ AFTER
          </h3>
          
          <div style={{ 
            background: "#f8f9fa", 
            padding: 16, 
            borderRadius: 8, 
            marginBottom: 16,
            minHeight: 100,
            maxHeight: 300,
            overflow: "auto"
          }}>
            <pre style={{ 
              whiteSpace: "pre-wrap", 
              fontFamily: "monospace", 
              fontSize: 14,
              margin: 0,
              color: "#333"
            }}>
              {after.prompt}
            </pre>
          </div>
          
          <div style={{ marginBottom: 12 }}>
            <strong>Clarity:</strong> {renderStars(after.score)}
            <div style={{ fontSize: 24, fontWeight: 700, color: "#28a745", marginTop: 4 }}>
              {after.score}/10
            </div>
          </div>
          
          <div style={{ marginBottom: 12 }}>
            <strong style={{ color: "#28a745" }}>
              {after.fixes?.length || 0} improvements made:
            </strong>
            <ul style={{ 
              margin: "8px 0 0 0", 
              paddingLeft: 20, 
              fontSize: 13,
              lineHeight: 1.6
            }}>
              {after.fixes?.slice(0, 6).map((fix, i) => (
                <li key={i} style={{ color: "#155724" }}>✓ {fix}</li>
              ))}
            </ul>
          </div>
          
          <div style={{ 
            background: "#d4edda", 
            padding: 12, 
            borderRadius: 6,
            color: "#155724"
          }}>
            <strong>Expected Quality:</strong> {after.expected_quality_pct}%
          </div>
        </div>
      </div>
      
      {/* Action Buttons */}
      <div style={{ 
        display: "flex", 
        gap: 16, 
        marginTop: 32,
        justifyContent: "center"
      }}>
        <button
          onClick={handleShareImage}
          style={{
            padding: "14px 28px",
            fontSize: 18,
            fontWeight: 700,
            background: "#ffffff",
            color: "#667eea",
            border: "none",
            borderRadius: 10,
            cursor: "pointer",
            boxShadow: "0 4px 12px rgba(0,0,0,0.15)"
          }}
        >
          📸 Download & Share
        </button>
        
        <button
          onClick={() => {
            navigator.clipboard.writeText(after.prompt);
            alert("✅ Optimized prompt copied to clipboard!");
          }}
          style={{
            padding: "14px 28px",
            fontSize: 18,
            fontWeight: 700,
            background: "#28a745",
            color: "white",
            border: "none",
            borderRadius: 10,
            cursor: "pointer",
            boxShadow: "0 4px 12px rgba(0,0,0,0.15)"
          }}
        >
          📋 Copy Optimized Prompt
        </button>
      </div>
    </div>
  );
}

