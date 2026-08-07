import { Copy, Sparkles } from "lucide-react";

import { cn } from "@/lib/utils";
import MarkdownContent from "@/components/dashboard/MarkdownContent";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export default function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
  };

  return (
    <div className={cn("flex", role === "user" ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[90%] rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm",
          role === "user"
            ? "bg-[#2D3A4A] text-[#F8F1DF]"
            : "border border-[#E4D9BF] bg-white text-[#2D3A4A]",
        )}
      >
        <div className="mb-2 flex items-center justify-between gap-3 text-[11px] uppercase tracking-[0.16em] opacity-70">
          <span className="flex items-center gap-1.5">
            {role === "assistant" ? <Sparkles size={12} /> : null}
            {role === "assistant" ? "Ask Atlas" : "You"}
          </span>
          {timestamp ? <span>{timestamp}</span> : null}
        </div>
        {role === "assistant" ? (
          <div className="space-y-2">
            <MarkdownContent content={content} />
            <button
              type="button"
              onClick={handleCopy}
              className="inline-flex items-center gap-1 rounded-full border border-[#E4D9BF] px-2 py-1 text-[11px] text-[#2D3A4A] hover:bg-[#F8F1DF]"
            >
              <Copy size={11} /> Copy
            </button>
          </div>
        ) : (
          <div>{content}</div>
        )}
      </div>
    </div>
  );
}
