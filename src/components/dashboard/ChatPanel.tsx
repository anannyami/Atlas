import { useMemo, useRef, useState } from "react";
import { Trash2 } from "lucide-react";

import ChatInput from "@/components/dashboard/ChatInput";
import ChatWindow from "@/components/dashboard/ChatWindow";
import SuggestedQuestions from "@/components/dashboard/SuggestedQuestions";
import { ConversationProvider, useConversation } from "@/context/ConversationContext";
import { AtlasChatService, type ChatMessage } from "@/services/AtlasChatService";

function ChatPanelContent() {
  const { messages, addMessage, clearMessages } = useConversation();
  const [loading, setLoading] = useState(false);
  const requestInFlight = useRef(false);

  const analysisPayload = useMemo(() => {
    const storedAnalysis = sessionStorage.getItem("atlas-analysis");
    return storedAnalysis ? (JSON.parse(storedAnalysis) as Record<string, unknown>) : null;
  }, []);

  const handleSend = async (value: string) => {
    if (requestInFlight.current) return;
    const timestamp = new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
    const userMessage: ChatMessage = { role: "user", content: value, timestamp };
    addMessage(userMessage);

    if (!analysisPayload) {
      addMessage({
        role: "assistant",
        content: "Analyze a repository before asking Atlas a question.",
        timestamp,
      });
      return;
    }

    requestInFlight.current = true;
    setLoading(true);

    try {
      const response = await AtlasChatService.ask({
        question: value,
        analysis: analysisPayload,
        conversation: [...messages, userMessage],
      });
      addMessage({
        role: "assistant",
        content: response.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }),
      });
    } catch (error) {
      addMessage({
        role: "assistant",
        content: "The assistant could not answer right now. Please try again in a moment.",
        timestamp: new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }),
      });
      console.error(error);
    } finally {
      requestInFlight.current = false;
      setLoading(false);
    }
  };

  return (
    <section className="rounded-3xl border border-[#E4D9BF] bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-[#2D3A4A]">Ask Atlas</h2>
          <p className="mt-1 text-sm text-[#5F6B72]">
            Ask questions grounded in the repository analysis that Atlas already produced.
          </p>
        </div>
        <button
          type="button"
          onClick={clearMessages}
          className="inline-flex items-center gap-1 rounded-full border border-[#E4D9BF] px-3 py-1.5 text-sm text-[#2D3A4A] hover:bg-[#F8F1DF]"
        >
          <Trash2 size={14} /> Clear
        </button>
      </div>
      <SuggestedQuestions onSelect={handleSend} />
      <div className="mt-4">
        <ChatWindow messages={messages} typing={loading} />
      </div>
      <div className="mt-4">
        <ChatInput onSend={handleSend} disabled={loading} />
      </div>
    </section>
  );
}

export default function ChatPanel() {
  return (
    <ConversationProvider>
      <ChatPanelContent />
    </ConversationProvider>
  );
}
