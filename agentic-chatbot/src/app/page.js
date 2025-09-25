import ChatPageClient from "./ChatPageClient";

export const dynamic = "force-dynamic";

function isUiEnabled() {
  const rawFlag =
    process.env.CHATBOT_UI_ENABLED ??
    process.env.NEXT_PUBLIC_CHATBOT_UI_ENABLED ??
    "true";
  return String(rawFlag).toLowerCase() !== "false";
}

function DisabledMessage() {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 24,
        textAlign: "center",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <div>
        <h1 style={{ fontSize: 24, marginBottom: 12 }}>Chatbot UI Disabled</h1>
        <p style={{ fontSize: 16, color: "#4b5563" }}>
          This deployment exposes only the agentic chatbot APIs. Integrate the
          shared UI component with <code>/api/chat</code> and <code>/api/mcp-status</code>
          to access the assistant.
        </p>
      </div>
    </div>
  );
}

export default function Page() {
  if (!isUiEnabled()) {
    return <DisabledMessage />;
  }
  return <ChatPageClient />;
}
