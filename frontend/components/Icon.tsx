export type IconName =
  | "alert"
  | "arrow"
  | "bell"
  | "calendar"
  | "change"
  | "check"
  | "chevron"
  | "clock"
  | "dashboard"
  | "data"
  | "design"
  | "document"
  | "estimate"
  | "export"
  | "filter"
  | "help"
  | "lock"
  | "mail"
  | "more"
  | "plus"
  | "prd"
  | "requirements"
  | "search"
  | "sessions"
  | "settings"
  | "shield"
  | "spark"
  | "upload";

const paths: Record<IconName, string[]> = {
  alert: ["M12 9v4", "M12 17h.01", "M10.3 4.5 2.6 18a2 2 0 0 0 1.7 3h15.4a2 2 0 0 0 1.7-3L13.7 4.5a2 2 0 0 0-3.4 0Z"],
  arrow: ["M5 12h14", "M13 5l7 7-7 7"],
  bell: ["M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9", "M10 21h4"],
  calendar: ["M8 2v4", "M16 2v4", "M3 10h18", "M5 4h14a2 2 0 0 1 2 2v14H3V6a2 2 0 0 1 2-2Z"],
  change: ["M7 7h10l-3-3", "M17 17H7l3 3", "M7 7v4", "M17 13v4"],
  check: ["M20 6 9 17l-5-5"],
  chevron: ["M9 18l6-6-6-6"],
  clock: ["M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20Z", "M12 6v6l4 2"],
  dashboard: ["M4 13h7V4H4v9Z", "M13 20h7V4h-7v16Z", "M4 20h7v-5H4v5Z"],
  data: ["M12 3c4.4 0 8 1.3 8 3s-3.6 3-8 3-8-1.3-8-3 3.6-3 8-3Z", "M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6", "M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"],
  design: ["M4 5h16v11H4V5Z", "M8 21h8", "M12 16v5"],
  document: ["M7 3h7l5 5v13H7V3Z", "M14 3v6h5", "M9 13h6", "M9 17h6"],
  estimate: ["M7 3h10v18H7V3Z", "M9 7h6", "M9 11h6", "M9 15h2", "M14 15h1"],
  export: ["M7 7V5h12v14H7v-2", "M3 12h10", "M9 8l4 4-4 4"],
  filter: ["M4 5h16l-6 7v5l-4 2v-7L4 5Z"],
  help: ["M9.5 9a2.5 2.5 0 1 1 4.2 1.8c-1.2.8-1.7 1.3-1.7 2.7", "M12 17h.01", "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20Z"],
  lock: ["M6 10h12v11H6V10Z", "M8 10V7a4 4 0 0 1 8 0v3"],
  mail: ["M4 6h16v12H4V6Z", "m4 7 8 6 8-6"],
  more: ["M5 12h.01", "M12 12h.01", "M19 12h.01"],
  plus: ["M12 5v14", "M5 12h14"],
  prd: ["M8 4h8l4 4v12H8V4Z", "M16 4v4h4", "M11 13h6", "M11 17h4"],
  requirements: ["M8 4h8l4 4v12H8V4Z", "M16 4v4h4", "M4 8v12h4", "M11 13h5", "M11 17h4"],
  search: ["M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15Z", "M16 16l5 5"],
  sessions: ["M4 7h16", "M4 12h16", "M4 17h10", "M6 4h12a2 2 0 0 1 2 2v14H4V6a2 2 0 0 1 2-2Z"],
  settings: ["M12 15.5A3.5 3.5 0 1 0 12 8a3.5 3.5 0 0 0 0 7.5Z", "M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2 3.4-.2-.1a1.7 1.7 0 0 0-1.9.3l-.7.4a1.7 1.7 0 0 0-1.3 1H10.3a1.7 1.7 0 0 0-1.3-1l-.7-.4a1.7 1.7 0 0 0-1.9-.3l-.2.1-2-3.4.1-.1A1.7 1.7 0 0 0 4.6 15l-.1-.8a1.7 1.7 0 0 0-1.1-1.5V9.3a1.7 1.7 0 0 0 1.1-1.5l.1-.8a1.7 1.7 0 0 0-.3-1.9l-.1-.1 2-3.4.2.1a1.7 1.7 0 0 0 1.9-.3L9 1a1.7 1.7 0 0 0 1.3-1h3.4A1.7 1.7 0 0 0 15 1l.7.4a1.7 1.7 0 0 0 1.9.3l.2-.1 2 3.4-.1.1a1.7 1.7 0 0 0-.3 1.9l.1.8a1.7 1.7 0 0 0 1.1 1.5v3.4a1.7 1.7 0 0 0-1.1 1.5l-.1.8Z"],
  shield: ["M12 3 20 6v6c0 5-3.4 8.4-8 9-4.6-.6-8-4-8-9V6l8-3Z", "M9 12l2 2 4-5"],
  spark: ["M12 2l1.6 5.2L19 9l-5.4 1.8L12 16l-1.6-5.2L5 9l5.4-1.8L12 2Z", "M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15Z"],
  upload: ["M12 16V4", "M7 9l5-5 5 5", "M5 20h14"],
};

export function Icon({ name }: { name: IconName }) {
  return (
    <svg className="icon" viewBox="0 0 24 24" aria-hidden="true">
      {paths[name].map((path) => (
        <path key={path} d={path} />
      ))}
    </svg>
  );
}
