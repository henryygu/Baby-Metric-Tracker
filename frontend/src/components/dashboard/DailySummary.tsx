import * as React from 'react';
import { Info } from 'lucide-react';
import { format } from 'date-fns';
import { BabyConfig, FeedStats, DiaperStats } from '../../types';

interface DailySummaryProps {
    config: BabyConfig;
    feeding: FeedStats;
    diapers: DiaperStats;
}

export const DailySummary: React.FC<DailySummaryProps> = ({ config, feeding, diapers }) => {
    return (
        <div className="card p-6 bg-slate-100 border-slate-200">
            <h3 className="font-bold mb-4 flex items-center gap-2 text-slate-800">
                <Info className="w-5 h-5 text-primary-600" />
                Daily Summary
            </h3>
            <div className="space-y-4">
                <div className="flex justify-between items-center py-2 border-b border-slate-200">
                    <span className="text-slate-600 font-medium">Avg Feed Duration</span>
                    <span className="font-bold text-slate-900">{feeding.today_avg} min</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-slate-200">
                    <span className="text-slate-600 font-medium">Total Diapers</span>
                    <span className="font-bold text-primary-600">{diapers.total.today_count}</span>
                </div>
                <p className="text-xs text-slate-500 mt-4 leading-relaxed">
                    Tracking since {format(new Date(config.date_of_birth), 'MMM dd, yyyy')}.
                    Baby {config.name} is growing healthy!
                </p>
            </div>
        </div>
    );
};
