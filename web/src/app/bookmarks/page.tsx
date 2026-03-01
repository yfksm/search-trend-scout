'use client';

import useSWR from 'swr';
import { fetcher } from '@/lib/api';
import ItemCard from '@/components/ItemCard';
import { Bookmark } from 'lucide-react';

export default function Bookmarks() {
    const { data: items, error, mutate, isLoading } = useSWR('/api/bookmarks', fetcher);

    return (
        <div className="p-8 max-w-5xl mx-auto space-y-12">

            <div className="flex items-center justify-between pb-6 border-b border-border">
                <div>
                    <h1 className="text-4xl font-extrabold tracking-tight flex items-center gap-4 mb-2">
                        <Bookmark className="text-primary" size={32} />
                        Bookmarks
                    </h1>
                    <p className="text-muted text-lg">Your saved content for deep diving.</p>
                </div>
            </div>

            <div className="space-y-6">
                {isLoading ? (
                    <div className="animate-pulse flex flex-col gap-6">
                        {[1, 2].map(i => <div key={i} className="h-48 glass-panel rounded-2xl" />)}
                    </div>
                ) : error ? (
                    <div className="text-red-400">Failed to load bookmarks.</div>
                ) : items?.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {items.map((item: any) => (
                            <ItemCard key={item.id} item={item} mutate={mutate} />
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-20 text-muted glass-panel rounded-2xl">
                        You haven't bookmarked any items yet.
                    </div>
                )}
            </div>

        </div>
    );
}
