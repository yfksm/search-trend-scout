'use client';

import { Settings as SettingsIcon, Database, Cpu } from 'lucide-react';

export default function Settings() {
    return (
        <div className="p-8 max-w-4xl mx-auto space-y-12">

            <div className="flex items-center justify-between pb-6 border-b border-border">
                <div>
                    <h1 className="text-4xl font-extrabold tracking-tight flex items-center gap-4 mb-2">
                        <SettingsIcon className="text-primary" size={32} />
                        Settings
                    </h1>
                    <p className="text-muted text-lg">Manage your ingestion sources and LLM preferences (MVP Preview).</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

                <div className="glass-panel p-6 rounded-2xl space-y-4">
                    <div className="flex items-center gap-3 font-bold text-xl mb-6 pb-4 border-b border-border">
                        <Database className="text-secondary" /> Data Sources
                    </div>
                    <p className="text-muted text-sm mb-4">
                        In MVP Phase 1, sources are predefined in the database.
                        Currently tracking default search engineering RSS feeds.
                    </p>
                    <div className="space-y-3">
                        <div className="flex justify-between items-center p-3 bg-card border border-border rounded-xl">
                            <span className="font-medium">arXiv CS.IR</span>
                            <span className="text-xs px-2 py-1 bg-emerald-500/20 text-emerald-500 rounded-lg">Active</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-card border border-border rounded-xl">
                            <span className="font-medium">Google Search Central Blog</span>
                            <span className="text-xs px-2 py-1 bg-emerald-500/20 text-emerald-500 rounded-lg">Active</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-card border border-border rounded-xl opacity-50">
                            <span className="font-medium text-muted">Add New Source...</span>
                            <span className="text-xs px-2 py-1 bg-border text-muted rounded-lg">Phase 2</span>
                        </div>
                    </div>
                </div>

                <div className="glass-panel p-6 rounded-2xl space-y-4">
                    <div className="flex items-center gap-3 font-bold text-xl mb-6 pb-4 border-b border-border">
                        <Cpu className="text-amber-500" /> Scoring & AI
                    </div>
                    <div className="space-y-4 text-sm text-muted">
                        <div>
                            <label className="block text-foreground font-medium mb-1">LLM Provider</label>
                            <select disabled className="w-full bg-card border border-border p-3 rounded-xl opacity-70 cursor-not-allowed">
                                <option>OpenAI (Environment Default)</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-foreground font-medium mb-1">Impact Signal Multiplier</label>
                            <input disabled type="range" className="w-full opacity-70 cursor-not-allowed" />
                        </div>
                        <p className="italic mt-4 text-xs">
                            Scoring weights and LLM keys are configured directly via `.env` in this minimal launch phase.
                        </p>
                    </div>
                </div>

            </div>

        </div>
    );
}
