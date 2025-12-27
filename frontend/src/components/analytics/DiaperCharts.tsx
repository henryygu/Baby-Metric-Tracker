import * as React from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { HistoryData } from '../../types';

interface DiaperChartsProps {
    history: HistoryData;
}

export const DiaperCharts: React.FC<DiaperChartsProps> = ({ history }) => {
    return (
        <div className="h-80">
            <h4 className="text-sm font-bold text-slate-500 mb-4 uppercase tracking-widest">Diapers by Type (Last 7 Days)</h4>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={history.diaper?.slice().reverse().map((h: any) => ({
                    date: h.date,
                    Pee: h.details.Pee,
                    Poop: h.details.Poop,
                    Mixed: h.details.Mixed
                }))}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="date" axisLine={false} tickLine={false} tickFormatter={(v: string) => v.split('-').slice(1).join('/')} />
                    <YAxis axisLine={false} tickLine={false} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="Pee" stackId="a" fill="#0ea5e9" />
                    <Bar dataKey="Poop" stackId="a" fill="#10b981" />
                    <Bar dataKey="Mixed" stackId="a" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};
