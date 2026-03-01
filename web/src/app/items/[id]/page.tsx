'use client';

import { useParams, useRouter } from 'next/navigation';
import useSWR from 'swr';
import { fetchItemDetail, toggleBookmark, markAsRead } from '@/lib/api';
import { ArrowLeft, ExternalLink, Bookmark, CheckCircle, ShieldAlert, Zap, Target } from 'lucide-react';
import { format } from 'date-fns';
import { useEffect, useState } from 'react';

export default function ItemDetail() {
    const params = useParams();
    const router = useRouter();
    const id = params.id as string;

    const { data: item, error, mutate } = useSWR(id ? `/api/items/${id}` : null, () => fetchItemDetail(id));
    const [isRead, setIsRead] = useState(false);

    useEffect(() => {
        if (item && !item.is_read) {
            markAsRead(item.id).then(() => {
                setIsRead(true);
                mutate();
            });
        } else if (item?.is_read) {
            setIsRead(true);
        }
    }, [item, mutate]);

    if (error) return <div className="p-8 text-red-400">Error loading details.</div>;
    if (!item) return <div className="p-8 animate-pulse text-muted">Loading...</div>;

    return (
        <div className="p-8 max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">

            {/* Back Button */}
            <button onClick={() => router.back()} className="flex items-center gap-2 text-muted hover:text-foreground transition-colors group">
                <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
                Back
            </button>

            {/* Header Info */}
            <header className="space-y-4">
                <div className="flex flex-wrap items-center gap-3 text-sm">
                    <span className="px-3 py-1 bg-primary/10 text-primary border border-primary/20 rounded-lg uppercase tracking-wider font-bold">
                        {item.lane || 'Uncategorized'}
                    </span>
                    <span className="text-muted font-medium">{item.site}</span>
                    <span className="text-muted">•</span>
                    <span className="text-muted">{item.published_at ? format(new Date(item.published_at), 'PPP') : 'Unknown Date'}</span>
                    <span className="text-muted">•</span>
                    <span className="text-amber-500 font-bold px-2 py-0.5 bg-amber-500/10 rounded-md">
                        🔥 Score: {item.score.toFixed(2)}
                    </span>
                </div>

                <h1 className="text-4xl font-extrabold leading-tight">
                    {item.title}
                </h1>

                <div className="flex flex-wrap gap-2 pt-2">
                    {item.tags?.map((t: any) => (
                        <span key={t.id} className="text-xs px-2.5 py-1 bg-card border border-border rounded-md text-muted">
                            #{t.name}
                        </span>
                    ))}
                </div>
            </header>

            {/* Actions */}
            <div className="flex gap-4 p-4 glass-panel rounded-2xl">
                <a
                    href={item.url} target="_blank" rel="noopener noreferrer"
                    className="flex-1 flex justify-center items-center gap-2 bg-primary text-white font-semibold py-3 rounded-xl hover:bg-primary/90 hover-lift"
                >
                    Read Original Source <ExternalLink size={18} />
                </a>
                <button
                    onClick={async () => {
                        await toggleBookmark(item.id, item.is_bookmarked);
                        mutate();
                    }}
                    className={`px-6 py-3 rounded-xl font-semibold border transition-all flex items-center justify-center ${item.is_bookmarked ? 'bg-primary/20 text-primary border-primary/30' : 'bg-transparent text-foreground border-border hover:bg-card'}`}
                >
                    <Bookmark size={18} fill={item.is_bookmarked ? "currentColor" : "none"} />
                </button>
            </div>

            {/* Core Insights */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-emerald-500 space-y-3">
                    <div className="flex items-center gap-2 text-emerald-500 font-bold mb-4">
                        <Target size={20} /> Why Important
                    </div>
                    <p className="text-lg leading-relaxed">{item.why_important}</p>
                </div>

                <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-rose-500 space-y-3">
                    <div className="flex items-center gap-2 text-rose-500 font-bold mb-4">
                        <ShieldAlert size={20} /> Trade-offs
                    </div>
                    <p className="text-lg leading-relaxed">{item.tradeoffs}</p>
                </div>

            </div>

            {/* TLDR & Bullets */}
            <div className="glass-panel p-8 rounded-2xl space-y-6">
                <div>
                    <h3 className="text-xl font-bold flex items-center gap-2 mb-4">
                        <Zap className="text-amber-500" /> TL;DR
                    </h3>
                    <p className="text-muted leading-relaxed text-lg">{item.summary_tldr}</p>
                </div>

                {item.summary_bullets && item.summary_bullets.length > 0 && (
                    <div className="pt-4 border-t border-border">
                        <h3 className="text-lg font-bold mb-4">Key Takeaways</h3>
                        <ul className="space-y-3">
                            {item.summary_bullets.map((b: string, i: number) => (
                                <li key={i} className="flex gap-3 text-muted">
                                    <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
                                    <span className="leading-relaxed">{b}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

        </div>
    );
}
