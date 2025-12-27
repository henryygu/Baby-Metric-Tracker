import * as React from 'react';
import { useState } from 'react';
import { ChefHat, Droplets, Baby, Moon } from 'lucide-react';

import { useDashboardData } from './hooks/useDashboardData';
import { formatAge, AgeFormat } from './utils/babyUtils';

// Components
import { Sidebar } from './components/common/Sidebar';
import { MetricCard } from './components/dashboard/MetricCard';
import { SessionTrackers } from './components/dashboard/SessionTrackers';
import { DiaperQuickLog } from './components/dashboard/DiaperQuickLog';
import { GrowthTracker } from './components/dashboard/GrowthTracker';
import { DailySummary } from './components/dashboard/DailySummary';
import { LogTable } from './components/logs/LogTable';
import { EditLogModal } from './components/logs/EditLogModal';

// Analytics Components
import { FeedingCharts } from './components/analytics/FeedingCharts';
import { SleepPredictionChart } from './components/analytics/SleepPredictionChart';
import { DiaperCharts } from './components/analytics/DiaperCharts';
import { GrowthCharts } from './components/analytics/GrowthCharts';

import { Log } from './types';

function App() {
    const {
        data,
        logs,
        config,
        loading,
        fetchData,
        logEvent,
        updateLog,
        stopSession,
        deleteLog
    } = useDashboardData();

    const [activeTab, setActiveTab] = useState<'dashboard' | 'analytics' | 'logs'>('dashboard');
    const [ageFormat, setAgeFormat] = useState<AgeFormat>('days');
    const [chartTab, setChartTab] = useState<'feeding' | 'sleep' | 'diaper' | 'growth'>('feeding');
    const [editingLog, setEditingLog] = useState<Log | null>(null);

    const cycleAgeFormat = () => {
        const formats: AgeFormat[] = ['days', 'months', 'years', 'complex'];
        const currentIndex = formats.indexOf(ageFormat);
        setAgeFormat(formats[(currentIndex + 1) % formats.length]);
    };

    if (loading || !data || !config) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50">
                <div className="flex flex-col items-center gap-4">
                    <Baby className="w-12 h-12 text-primary-600 animate-bounce" />
                    <p className="text-slate-500 font-medium">Loading Dashboard...</p>
                </div>
            </div>
        );
    }

    const { feeding, diapers, ongoing_feed, ongoing_sleep, last_completed_feed, history } = data;

    return (
        <div className="min-h-screen flex flex-col md:flex-row bg-slate-50 text-slate-900">
            <Sidebar
                config={config}
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                ageFormatString={formatAge(config, ageFormat)}
                onCycleAgeFormat={cycleAgeFormat}
                onRefresh={fetchData}
            />

            <main className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full overflow-y-auto">
                {activeTab === 'dashboard' ? (
                    <div className="space-y-8">
                        <SessionTrackers
                            ongoingFeed={ongoing_feed}
                            ongoingSleep={ongoing_sleep}
                            lastCompletedFeed={last_completed_feed}
                            onStartFeed={(o) => logEvent('Feeding', { orientation: o, details: 'ongoing' })}
                            onStopFeed={() => stopSession('Feeding')}
                            onStartSleep={() => logEvent('Sleep', { details: 'ongoing' })}
                            onStopSleep={() => stopSession('Sleep')}
                        />

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            <MetricCard
                                title="Feeds Today"
                                value={feeding.today_count}
                                delta={feeding.count_delta}
                                icon={<ChefHat className="w-5 h-5 text-orange-500" />}
                                color="orange"
                                subtitle={`${feeding.today_duration} min total`}
                            />
                            <MetricCard
                                title="Diapers Total"
                                value={diapers.total.today_count}
                                delta={diapers.total.delta}
                                icon={<Droplets className="w-5 h-5 text-blue-500" />}
                                color="blue"
                                subtitle={`Last: ${diapers.last_time_str} ago`}
                            />
                            <MetricCard
                                title="Last Pee"
                                value={diapers.last_pee_str ?? '---'}
                                delta={0}
                                icon={<Droplets className="w-5 h-5 text-emerald-500" />}
                                color="emerald"
                                subtitle="Since last wet"
                            />
                            <MetricCard
                                title="Last Poop"
                                value={diapers.last_poop_str ?? '---'}
                                delta={0}
                                icon={<Droplets className="w-5 h-5 text-indigo-500" />}
                                color="indigo"
                                subtitle="Since last dirty"
                            />
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            <DiaperQuickLog onLog={logEvent} />
                            <div className="space-y-6">
                                <GrowthTracker onRecord={(w, h) => logEvent('Growth', {
                                    weight: w,
                                    height: h,
                                    details: `${w ? w + 'kg' : ''}${w && h ? ', ' : ''}${h ? h + 'cm' : ''}`
                                })} />
                                <DailySummary config={config} feeding={feeding} diapers={diapers} />
                            </div>
                        </div>

                        {editingLog && (
                            <EditLogModal
                                log={editingLog}
                                onClose={() => setEditingLog(null)}
                                onSave={(id, data) => {
                                    updateLog(id, data);
                                    setEditingLog(null);
                                }}
                            />
                        )}
                    </div>
                ) : activeTab === 'analytics' ? (
                    <div className="space-y-8">
                        <div className="flex items-center justify-between">
                            <h2 className="text-2xl font-bold tracking-tight">Analytics & Trends</h2>
                        </div>

                        <div className="card overflow-hidden">
                            <div className="flex border-b border-slate-100 bg-slate-50/50">
                                <button
                                    onClick={() => setChartTab('feeding')}
                                    className={`px-6 py-4 text-sm font-bold flex items-center gap-2 border-b-2 transition-all ${chartTab === 'feeding' ? 'bg-white border-orange-500 text-orange-600' : 'border-transparent text-slate-500'}`}
                                >
                                    <ChefHat className="w-4 h-4" /> Feeding
                                </button>
                                <button
                                    onClick={() => setChartTab('sleep')}
                                    className={`px-6 py-4 text-sm font-bold flex items-center gap-2 border-b-2 transition-all ${chartTab === 'sleep' ? 'bg-white border-indigo-500 text-indigo-600' : 'border-transparent text-slate-500'}`}
                                >
                                    <Moon className="w-4 h-4" /> Sleep
                                </button>
                                <button
                                    onClick={() => setChartTab('diaper')}
                                    className={`px-6 py-4 text-sm font-bold flex items-center gap-2 border-b-2 transition-all ${chartTab === 'diaper' ? 'bg-white border-blue-500 text-blue-600' : 'border-transparent text-slate-500'}`}
                                >
                                    <Droplets className="w-4 h-4" /> Diapers
                                </button>
                                <button
                                    onClick={() => setChartTab('growth')}
                                    className={`px-6 py-4 text-sm font-bold flex items-center gap-2 border-b-2 transition-all ${chartTab === 'growth' ? 'bg-white border-emerald-500 text-emerald-600' : 'border-transparent text-slate-500'}`}
                                >
                                    <Baby className="w-4 h-4" /> Growth
                                </button>
                            </div>

                            <div className="p-6">
                                {chartTab === 'feeding' && <FeedingCharts history={history} />}
                                {chartTab === 'sleep' && <SleepPredictionChart data={data} />}
                                {chartTab === 'diaper' && <DiaperCharts history={history} />}
                                {chartTab === 'growth' && <GrowthCharts history={history} />}
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="space-y-6">
                        <div className="flex items-center justify-between">
                            <h2 className="text-2xl font-bold tracking-tight">Activity History</h2>
                        </div>
                        <LogTable
                            logs={logs}
                            onEdit={setEditingLog}
                            onDelete={deleteLog}
                        />
                        {editingLog && (
                            <EditLogModal
                                log={editingLog}
                                onClose={() => setEditingLog(null)}
                                onSave={(id, data) => {
                                    updateLog(id, data);
                                    setEditingLog(null);
                                }}
                            />
                        )}
                    </div>
                )}
            </main>
        </div>
    );
}

export default App;
