import * as React from 'react';
import { useMemo, Fragment } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
    AreaChart, Area
} from 'recharts';
import { Moon } from 'lucide-react';
import { transformSleepData } from '../../utils/sleepUtils';
import { DashboardData } from '../../types';

interface SleepPredictionChartProps {
    data: DashboardData;
}

export const SleepPredictionChart: React.FC<SleepPredictionChartProps> = ({ data }) => {
    const sleepScheduleData = useMemo(() => {
        if (!data.predictions?.sleep) return [];
        return transformSleepData(data.predictions.sleep.past, data.predictions.sleep.future);
    }, [data.predictions?.sleep]);

    return (
        <div className="space-y-12">
            <div>
                <div className="flex items-center justify-between mb-4">
                    <h4 className="text-sm font-bold text-slate-500 uppercase tracking-widest">Sleep Schedule + Prediction (14 Day View)</h4>
                    <div className="flex gap-4 text-xs font-medium">
                        <span className="flex items-center gap-2"><div className="w-3 h-3 bg-indigo-500 rounded"></div> Actual</span>
                        <span className="flex items-center gap-2"><div className="w-3 h-3 bg-indigo-200 rounded"></div> Predicted</span>
                    </div>
                </div>
                <div className="h-[500px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                            data={sleepScheduleData}
                            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                        >
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                            <XAxis
                                dataKey="date"
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: '#64748b', fontSize: 10 }}
                            />
                            <YAxis
                                type="number"
                                domain={[0, 1440]}
                                ticks={[0, 480, 720, 960, 1200, 1440]}
                                tickFormatter={(v) => `${Math.floor(v / 60)}:00`}
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: '#64748b', fontSize: 10 }}
                                reversed
                            />
                            <Tooltip
                                formatter={(value: any, name: any, props: any) => {
                                    const key = props.dataKey;
                                    if (key && typeof key === 'string' && key.startsWith('sleep_')) {
                                        const index = key.split('_')[1];
                                        return props.payload[`label_${index}`];
                                    }
                                    return null;
                                }}
                                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                            />
                            {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map(i => (
                                <Fragment key={i}>
                                    <Bar dataKey={`gap_${i}`} stackId="a" fill="transparent" />
                                    <Bar dataKey={`sleep_${i}`} stackId="a">
                                        {sleepScheduleData.map((entry, idx) => (
                                            <Cell
                                                key={`cell-${idx}`}
                                                fill={entry[`is_predicted_${i}`] ? '#c7d2fe' : '#6366f1'}
                                            />
                                        ))}
                                    </Bar>
                                </Fragment>
                            ))}
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {data.predictions?.sleep?.summary && (
                    <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Developmental Stage</div>
                            <div className="text-xl font-bold text-indigo-600">{data.predictions.sleep.summary.stage}</div>
                            <div className="text-xs text-slate-500 mt-1">Based on baby's age</div>
                        </div>
                        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Daily Predicted Naps</div>
                            <div className="text-xl font-bold text-indigo-600">{data.predictions.sleep.summary.nap_count} Naps</div>
                            <div className="text-xs text-slate-500 mt-1">Excluding night sleep</div>
                        </div>
                        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Total Daily Sleep</div>
                            <div className="text-xl font-bold text-indigo-600">{data.predictions.sleep.summary.total_hours} Hours</div>
                            <div className="text-xs text-slate-500 mt-1">Predicted average</div>
                        </div>

                        <div className="md:col-span-3 bg-indigo-50/50 p-6 rounded-2xl border border-indigo-100">
                            <h5 className="font-bold text-indigo-900 mb-4 flex items-center gap-2">
                                <Moon className="w-4 h-4" />
                                Predicted Routine Breakdown
                            </h5>
                            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                                {data.predictions.sleep.summary.details.map((slot: any, idx: number) => (
                                    <div key={idx} className="bg-white/60 backdrop-blur-sm p-3 rounded-lg border border-indigo-100">
                                        <div className="text-[10px] font-bold text-indigo-400 uppercase mb-1">{slot.type}</div>
                                        <div className="text-sm font-bold text-indigo-900">{slot.start} - {slot.end}</div>
                                        <div className="text-xs text-indigo-600 font-medium">{slot.duration}h duration</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <div className="h-64">
                <h4 className="text-sm font-bold text-slate-500 mb-4 uppercase tracking-widest">Daily Sleep Total (Hours)</h4>
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data.history?.sleep?.slice().reverse() || []}>
                        <defs>
                            <linearGradient id="colorSleep" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.1} />
                                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="date" axisLine={false} tickLine={false} tickFormatter={(v) => v.split('-').slice(1).join('/')} />
                        <YAxis axisLine={false} tickLine={false} />
                        <Tooltip />
                        <Area type="monotone" dataKey="total_hours" stroke="#6366f1" fillOpacity={1} fill="url(#colorSleep)" />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};
