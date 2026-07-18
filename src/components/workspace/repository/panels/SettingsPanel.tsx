const groups = [
  { title: "Profile", desc: "Display name and avatar shown in the workspace." },
  { title: "Theme", desc: "Warm parchment is the only theme, for now." },
  { title: "Shortcuts", desc: "Customise the keys that open Search, Explorer, and Insights." },
  { title: "Appearance", desc: "Adjust density, typography scale, and motion." },
  { title: "Repository Preferences", desc: "Set the default panel and reading order for new repositories." },
];

export function SettingsPanel() {
  return (
    <div className="max-w-2xl mx-auto px-10 py-10">
      <div className="text-[10.5px] font-mono uppercase tracking-[0.16em] text-mulberry/55">Workspace</div>
      <h1 className="font-serif text-[40px] text-oxblood leading-tight mt-1">Settings</h1>

      <div className="mt-8 space-y-2">
        {groups.map((g) => (
          <button
            key={g.title}
            className="w-full text-left acrylic p-5 hover:border-oxblood/25 transition"
          >
            <div className="font-serif text-[20px] text-oxblood">{g.title}</div>
            <div className="text-[13px] text-mulberry/70 mt-0.5">{g.desc}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
