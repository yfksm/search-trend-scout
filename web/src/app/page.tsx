"use client";

import { useState, useEffect } from "react";
import useSWR from "swr";
import { fetchFeed, triggerIngestion, getIngestionStatus } from "@/lib/api";
import ItemCard from "@/components/ItemCard";
import { Sparkles, Activity, RefreshCw, FilterX } from "lucide-react";
import { format } from "date-fns";

export default function Home() {
  const [lane, setLane] = useState<string>("");
  const [tagFilter, setTagFilter] = useState<string>("");
  const [range, setRange] = useState<number>(7);
  const [isIngesting, setIsIngesting] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Auto poll status if ingesting
  const { data: status } = useSWR("/api/ingest/status", getIngestionStatus, {
    refreshInterval: isIngesting ? 2000 : 0,
  });

  if (isIngesting && status && !status.is_running) {
    setIsIngesting(false);
  }

  // Fetch feed data
  const { data, error, mutate, isLoading } = useSWR(
    ["/api/feed", lane, range, tagFilter],
    () => fetchFeed(tagFilter ? [tagFilter] : [], lane, range),
  );

  const handleRunIngestion = async () => {
    setIsIngesting(true);
    await triggerIngestion();
    mutate();
  };

  const handleClearFilters = () => {
    setLane("");
    setTagFilter("");
    setRange(7);
  };

  const items = data?.items || [];

  // Today's Brief = Top 5 items with score > 1.0 that are NOT read
  const unreadItems = items.filter((i: any) => !i.is_read);
  const briefItems = unreadItems.slice(0, 5);
  const remainingItems = items.slice(briefItems.length);

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-12">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-border">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight mb-2">
            Today in Search
          </h1>
          <p className="text-muted text-lg">
            {mounted ? format(new Date(), "EEEE, MMMM do") : "Today"} • The most
            important updates ranked for you.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRunIngestion}
            disabled={isIngesting || status?.is_running}
            className="flex items-center gap-2 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 transition-all font-semibold px-5 py-2.5 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed group"
          >
            <RefreshCw
              size={18}
              className={
                isIngesting || status?.is_running
                  ? "animate-spin"
                  : "group-hover:rotate-180 transition-transform duration-500"
              }
            />
            {isIngesting || status?.is_running
              ? "Ingesting..."
              : "Run Ingestion"}
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 glass-panel p-4 rounded-2xl">
        <div className="flex items-center gap-2 text-sm font-medium text-muted px-2">
          <FilterX size={16} /> Filters
        </div>

        <div className="h-6 w-px bg-border mx-2" />

        <div className="flex flex-wrap gap-2">
          {["", "research", "practice", "ecosystem"].map((l) => (
            <button
              key={`lane-${l}`}
              onClick={() => {
                setLane(l);
                setTagFilter("");
              }}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium capitalize transition-all border ${
                lane === l && tagFilter === ""
                  ? "bg-secondary/20 text-secondary border-secondary/30"
                  : "bg-transparent text-muted border-transparent hover:bg-card hover:text-foreground"
              }`}
            >
              {l || "All Lanes"}
            </button>
          ))}
          <div className="h-4 w-px bg-border/50 self-center mx-1" />
          <button
            onClick={() => {
              setLane("");
              setTagFilter("event");
            }}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all border ${
              tagFilter === "event"
                ? "bg-amber-500/20 text-amber-500 border-amber-500/30"
                : "bg-transparent text-muted border-transparent hover:bg-card hover:text-foreground"
            }`}
          >
            Events
          </button>
        </div>
      </div>

      {/* Today's Brief Section */}
      {!isLoading && !error && briefItems.length > 0 && (
        <section className="space-y-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-amber-500/20 p-2 rounded-xl border border-amber-500/30 shadow-[0_0_15px_rgba(245,158,11,0.2)]">
              <Sparkles className="text-amber-500" size={24} />
            </div>
            <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-amber-200 to-amber-500">
              Today's Brief
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-1 gap-6">
            {briefItems.map((item: any) => (
              <ItemCard key={item.id} item={item} mutate={mutate} />
            ))}
          </div>
        </section>
      )}

      {/* Main Feed Section */}
      <section className="space-y-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-primary/20 p-2 rounded-xl border border-primary/30">
            <Activity className="text-primary" size={24} />
          </div>
          <h2 className="text-2xl font-bold">Latest Feed</h2>
        </div>

        {isLoading ? (
          <div className="flex flex-col gap-6 animate-pulse">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-48 glass-panel rounded-2xl border border-border"
              />
            ))}
          </div>
        ) : error ? (
          <div className="p-8 text-center glass-panel rounded-2xl border-red-500/20 text-red-400">
            Failed to load feed. Is the API running?
          </div>
        ) : remainingItems.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
            {remainingItems.map((item: any) => (
              <ItemCard key={item.id} item={item} mutate={mutate} />
            ))}
          </div>
        ) : (
          <div className="text-center py-20 glass-panel rounded-2xl text-muted">
            <p className="text-lg mb-2">
              No items found matching your filters.
            </p>
            <button
              onClick={handleClearFilters}
              className="text-primary hover:underline"
            >
              Clear filters
            </button>
          </div>
        )}
      </section>
    </div>
  );
}
