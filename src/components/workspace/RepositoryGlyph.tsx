import type { Repository } from "@/lib/mock-repositories";

export function RepositoryCover({ repo, className = "" }: { repo: Repository; className?: string }) {
  const [a, b] = repo.accent;
  const id = `cov-${repo.id}`;
  return (
    <div className={`relative overflow-hidden rounded-2xl ${className}`}>
      <svg viewBox="0 0 400 200" className="w-full h-full block">
        <defs>
          <linearGradient id={id} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor={a} />
            <stop offset="1" stopColor={b} />
          </linearGradient>
          <radialGradient id={`${id}-glow`} cx="30%" cy="30%" r="60%">
            <stop offset="0" stopColor="#F0E6B1" stopOpacity="0.6" />
            <stop offset="1" stopColor="#F0E6B1" stopOpacity="0" />
          </radialGradient>
          <pattern id={`${id}-grid`} width="24" height="24" patternUnits="userSpaceOnUse">
            <path d="M24 0 L0 0 0 24" fill="none" stroke="#F0E6B1" strokeOpacity="0.12" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width="400" height="200" fill={`url(#${id})`} />
        <rect width="400" height="200" fill={`url(#${id}-grid)`} />
        <rect width="400" height="200" fill={`url(#${id}-glow)`} />
        <Glyph kind={repo.glyph} />
      </svg>
      <div className="absolute inset-0 pointer-events-none" style={{ boxShadow: "inset 0 1px 0 rgba(255,255,255,0.35), inset 0 -1px 0 rgba(0,0,0,0.15)" }} />
    </div>
  );
}

function Glyph({ kind }: { kind: Repository["glyph"] }) {
  const stroke = "#F5E9C8";
  switch (kind) {
    case "atom":
      return (
        <g transform="translate(200 100)" stroke={stroke} strokeWidth="1.4" fill="none" opacity="0.9">
          <circle r="14" fill={stroke} />
          <ellipse rx="55" ry="20" />
          <ellipse rx="55" ry="20" transform="rotate(60)" />
          <ellipse rx="55" ry="20" transform="rotate(-60)" />
        </g>
      );
    case "triangle":
      return (
        <g transform="translate(200 100)" fill={stroke} opacity="0.9">
          <path d="M0 -46 L46 34 L-46 34 Z" />
        </g>
      );
    case "square":
      return (
        <g transform="translate(200 100)" stroke={stroke} strokeWidth="1.4" fill="none" opacity="0.9">
          <rect x="-40" y="-30" width="80" height="60" rx="8" />
          <path d="M-40 -10 H40 M-10 -30 V30" />
        </g>
      );
    case "brain":
      return (
        <g transform="translate(200 100)" stroke={stroke} strokeWidth="1.3" fill="none" opacity="0.9">
          {Array.from({ length: 6 }).map((_, i) => (
            <circle key={i} r={10 + i * 8} />
          ))}
          <circle r="4" fill={stroke} />
        </g>
      );
    case "hex":
      return (
        <g transform="translate(200 100)" stroke={stroke} strokeWidth="1.4" fill="none" opacity="0.9">
          <path d="M-40 0 L-20 -34 L20 -34 L40 0 L20 34 L-20 34 Z" />
          <path d="M-20 0 L-10 -17 L10 -17 L20 0 L10 17 L-10 17 Z" />
        </g>
      );
    case "node":
      return (
        <g transform="translate(200 100)" stroke={stroke} strokeWidth="1.4" fill="none" opacity="0.9">
          <path d="M0 -40 L34 -20 L34 20 L0 40 L-34 20 L-34 -20 Z" />
          <path d="M0 -40 V40 M-34 -20 L34 20 M34 -20 L-34 20" opacity="0.5" />
        </g>
      );
    case "bolt":
      return (
        <g transform="translate(200 100)" fill={stroke} opacity="0.9">
          <path d="M-6 -40 L16 -6 L2 -4 L10 40 L-14 4 L0 2 Z" />
        </g>
      );
  }
}
