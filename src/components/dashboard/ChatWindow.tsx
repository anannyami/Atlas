import { useEffect, useMemo, useRef } from "react";

import ChatMessage from "@/components/dashboard/ChatMessage";
import type { ChatMessage as ChatMessageModel } from "@/services/AtlasChatService";

interface ChatWindowProps {
  messages: ChatMessageModel[];
  typing?: boolean;
}

export default function ChatWindow({ messages, typing }: ChatWindowProps) {
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const emptyState = useMemo(() => {
    if (messages.length > 0) return null;
    return (
      <div className="rounded-2xl border border-dashed border-[#E4D9BF] bg-[#F8F1DF]/60 p-4 text-sm text-[#2D3A4A]">
        Ask Atlas about the repository overview, architecture, stack, or health.
      </div>
    );
  }, [messages.length]);

  return (
    <div className="flex h-[360px] flex-col gap-3 overflow-y-auto rounded-2xl border border-[#E4D9BF] bg-[#FFFDF8] p-4">
      {emptyState}
      {messages.map((message, index) => (
        <ChatMessage
          key={`${message.role}-${index}`}
          role={message.role}
          content={message.content}
          timestamp={message.timestamp}
        />
      ))}
      {typing ? (
        <div className="flex justify-start">
          <div className="rounded-2xl border border-[#E4D9BF] bg-white px-4 py-3 text-sm text-[#2D3A4A]">
            Atlas is thinking…
          </div>
        </div>
      ) : null}
      <div ref={endRef} />
    </div>
  );
}
