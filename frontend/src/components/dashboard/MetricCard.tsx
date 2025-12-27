import * as React from 'react';

interface MetricCardProps {
    title: string;
    value: string | number;
    delta: number;
    icon: React.ReactNode;
    color: string;
    subtitle: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({ title, value, delta, icon, color, subtitle }) => {
    const isPositive = delta > 0;
    const isNeutral = delta === 0;

    const colorClasses: Record<string, string> = {
        orange: 'bg-orange-50 group-hover:bg-orange-100',
        blue: 'bg-blue-50 group-hover:bg-blue-100',
        emerald: 'bg-emerald-50 group-hover:bg-emerald-100',
        indigo: 'bg-indigo-50 group-hover:bg-indigo-100',
    };

    return (
        <div className="card p-5 group hover:border-primary-200">
            <div className="flex justify-between items-start mb-4">
                <div className={`p-2 rounded-lg transition-colors ${colorClasses[color] || 'bg-slate-50 group-hover:bg-slate-100'}`}>
                    {icon}
                </div>
                {!isNeutral && (
                    <span className={`text-xs font-bold px-2 py-1 rounded-full ${isPositive ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'}`}>
                        {isPositive ? '+' : ''}{delta}
                    </span>
                )}
            </div>
            <div>
                <p className="text-sm text-slate-500 font-medium mb-1">{title}</p>
                <div className="flex items-baseline gap-2">
                    <h4 className="text-2xl font-bold tracking-tight">{value}</h4>
                    <span className="text-xs text-slate-400 font-normal">{subtitle}</span>
                </div>
            </div>
        </div>
    );
};
