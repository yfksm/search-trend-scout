import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";
import { Home, Bookmark, Settings, Search, Radar } from "lucide-react";

export const metadata: Metadata = {
  title: "Search Trend Scout",
  description: "AI-Powered News Aggregator for Search Engineers",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="antialiased min-h-screen flex bg-[var(--background)] text-[var(--foreground)] selection:bg-primary/30">
        {/* Sidebar */}
        <aside className="w-64 glass-panel border-r border-border min-h-screen flex flex-col fixed left-0 top-0 z-50">
          <div className="p-6 flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20">
              <Radar size={18} className="text-white" />
            </div>
            <span className="font-bold tracking-tight text-lg">
              Trend Scout
            </span>
          </div>

          <nav className="flex-1 px-4 py-4 space-y-2">
            <NavItem href="/" icon={<Home size={20} />} label="Home Feed" />
            <NavItem
              href="/bookmarks"
              icon={<Bookmark size={20} />}
              label="Bookmarks"
            />
            <NavItem
              href="/settings"
              icon={<Settings size={20} />}
              label="Settings"
            />
          </nav>

          <div className="p-4 mt-auto">
            <div className="px-4 py-3 rounded-xl bg-card border border-border text-xs text-muted">
              v1.0 MVP
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 ml-64 min-h-screen relative max-w-7xl mx-auto w-full">
          {children}
        </main>
      </body>
    </html>
  );
}

function NavItem({
  href,
  icon,
  label,
}: {
  href: string;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 px-4 py-3 rounded-xl text-muted hover:text-foreground hover:bg-card hover:border-border border border-transparent transition-all group"
    >
      <span className="group-hover:text-primary transition-colors">{icon}</span>
      <span className="font-medium text-sm">{label}</span>
    </Link>
  );
}
