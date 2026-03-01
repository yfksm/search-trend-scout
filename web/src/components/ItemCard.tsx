"use client";

import { useState } from "react";
import Link from "next/link";
import { Bookmark, CheckCircle, ExternalLink, ArrowRight } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { toggleBookmark, markAsRead } from "@/lib/api";

export default function ItemCard({
  item,
  mutate,
}: {
  item: any;
  mutate?: () => void;
}) {
  const [isBookmarked, setIsBookmarked] = useState(item.is_bookmarked);
  const [isRead, setIsRead] = useState(item.is_read);

  const handleBookmark = async (e: React.MouseEvent) => {
    e.preventDefault();
    const newStatus = !isBookmarked;
    setIsBookmarked(newStatus);
    await toggleBookmark(item.id, !newStatus);
    if (mutate) mutate();
  };

  const handleRead = async (e: React.MouseEvent) => {
    if (isRead) return;
    setIsRead(true);
    await markAsRead(item.id);
    if (mutate) mutate();
  };

  const laneColors: Record<string, string> = {
    research: "bg-purple-500/10 text-purple-400 border-purple-500/20",
    practice: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    ecosystem: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  };

  const currentLaneColor = item.lane
    ? laneColors[item.lane]
    : "bg-gray-500/10 text-gray-400 border-gray-500/20";

  return (
    <div
      className={`relative flex flex-col glass-panel hover-lift p-5 rounded-2xl group transition-all duration-300 ${isRead ? "bg-card/40" : "bg-card/80"}`}
    >
      {/* Header Info */}
      <div className="flex items-center justify-between mb-3 text-sm">
        <div className="flex items-center gap-3">
          <span
            className={`px-2.5 py-1 text-xs font-semibold uppercase tracking-wider rounded-lg border ${currentLaneColor}`}
          >
            {item.lane || "Uncategorized"}
          </span>
          <span className="text-slate-300 font-medium">
            {item.site || "Unknown Source"}
          </span>
          <span className="text-border">•</span>
          <span className="text-slate-400">
            {item.published_at
              ? formatDistanceToNow(new Date(item.published_at), {
                  addSuffix: true,
                })
              : "Recently"}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {item.score >= 5.0 && (
            <div className="flex items-center gap-1.5 px-2 py-1 bg-amber-500/20 text-amber-500 rounded-lg text-xs font-bold border border-amber-500/30">
              🔥 {item.score.toFixed(1)}
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1">
        <Link href={`/items/${item.id}`} onClick={handleRead}>
          <h2
            className={`text-xl font-bold leading-tight mb-2 group-hover:text-primary transition-colors cursor-pointer ${isRead ? "text-slate-300" : "text-foreground"}`}
          >
            {item.title}
          </h2>
        </Link>
        <p className="text-sm font-medium text-slate-300 mb-4 italic border-l-2 border-primary/40 pl-3">
          {item.why_important || "Processing importance..."}
        </p>
      </div>

      {/* Tags */}
      {item.tags?.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {item.tags.slice(0, 4).map((tag: any) => (
            <span
              key={tag.id}
              className="text-xs px-2 py-1 rounded bg-border/50 text-muted"
            >
              #{tag.name}
            </span>
          ))}
          {item.tags.length > 4 && (
            <span className="text-xs px-2 py-1 text-muted">
              +{item.tags.length - 4}
            </span>
          )}
        </div>
      )}

      {/* Footer Actions */}
      <div className="flex items-center justify-between mt-auto pt-4 border-t border-border/50">
        <div className="flex items-center gap-1">
          <button
            onClick={handleBookmark}
            className={`p-2 rounded-xl transition-all ${isBookmarked ? "bg-primary/20 text-primary" : "text-muted hover:bg-card hover:text-foreground"}`}
            title="Bookmark"
          >
            <Bookmark size={18} fill={isBookmarked ? "currentColor" : "none"} />
          </button>

          <button
            onClick={handleRead}
            disabled={isRead}
            className={`p-2 rounded-xl transition-all ${isRead ? "text-emerald-500" : "text-muted hover:bg-card hover:text-foreground"}`}
            title="Mark as read"
          >
            <CheckCircle size={18} />
          </button>
        </div>

        <div className="flex gap-2">
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={handleRead}
            className="flex items-center gap-1.5 text-xs font-medium text-muted hover:text-primary transition-colors px-3 py-1.5 rounded-lg hover:bg-primary/10"
          >
            Source
            <ExternalLink size={14} />
          </a>
          <Link
            href={`/items/${item.id}`}
            onClick={handleRead}
            className="flex items-center gap-1.5 text-xs font-bold text-primary bg-primary/10 hover:bg-primary/20 transition-colors px-4 py-1.5 rounded-lg border border-primary/20"
          >
            Read Brief
            <ArrowRight size={14} />
          </Link>
        </div>
      </div>
    </div>
  );
}
