import { useState } from "react";

interface ChatInputProps {
  onSend: (value: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSubmit(event as unknown as React.FormEvent);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 border-t border-[#E4D9BF] bg-[#F8F1DF] p-3">
      <textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask about this repository..."
        rows={3}
        className="flex-1 resize-none rounded-xl border border-[#E4D9BF] bg-white px-3 py-2 text-sm outline-none focus:border-[#2D3A4A]"
        disabled={disabled}
      />
      <button
        type="submit"
        disabled={disabled}
        className="rounded-xl bg-[#2D3A4A] px-4 py-2 text-sm font-medium text-[#F8F1DF] disabled:opacity-60"
      >
        Send
      </button>
    </form>
  );
}
