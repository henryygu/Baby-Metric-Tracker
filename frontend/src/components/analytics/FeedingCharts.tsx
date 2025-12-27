import * as React from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { HistoryData } from '../../types';

interface FeedingChartsProps {
    history: HistoryData;
}

export const FeedingCharts: React.FC<FeedingChartsProps> = ({ history }) => {
    return (
        <div className="space-y-12">
            <div className="h-80">
                <h4 className="text-sm font-bold text-slate-500 mb-4 uppercase tracking-widest">Feeds Total per Day (Last 7 Days)</h4>
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={history.feeding?.slice().reverse()}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="date" axisLine={false} tickLine={false} tickFormatter={(v: string) => v.split('-').slice(1).join('/')} />
                        <YAxis axisLine={false} tickLine={false} />
                        <Tooltip />
                        <Bar dataKey="count" fill="#fbbf24" radius={[4, 4, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
            <div className="h-80">
                <h4 className="text-sm font-bold text-slate-500 mb-4 uppercase tracking-widest">Feeds by Orientation (Last 7 Days)</h4>
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={history.feeding?.slice().reverse().map((h: any) => ({
                        date: h.date,
                        Left: h.details.Left,
                        Right: h.details.Right,
                        Expressed: h.details.Expressed
                    }))}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="date" axisLine={false} tickLine={false} tickFormatter={(v: string) => v.split('-').slice(1).join('/')} />
                        <YAxis axisLine={false} tickLine={false} />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="Left" stackId="a" fill="#f59e0b" />
                        <Bar dataKey="Right" stackId="a" fill="#ea580c" />
                        <Bar dataKey="Expressed" stackId="a" fill="#78350f" radius={[4, 4, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};
