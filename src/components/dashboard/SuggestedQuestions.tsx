interface SuggestedQuestionsProps {
  onSelect: (value: string) => void;
}

const suggestions = [
  "What is this repository about?",
  "How is the architecture structured?",
  "What technologies are used here?",
  "How healthy is this repository?",
];

export default function SuggestedQuestions({ onSelect }: SuggestedQuestionsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {suggestions.map((question) => (
        <button
          key={question}
          type="button"
          onClick={() => onSelect(question)}
          className="rounded-full border border-[#E4D9BF] bg-white px-3 py-1.5 text-sm text-[#2D3A4A] transition hover:bg-[#F1E7CF]"
        >
          {question}
        </button>
      ))}
    </div>
  );
}
