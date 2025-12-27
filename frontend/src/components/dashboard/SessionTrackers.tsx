import * as React from 'react';
import { ChefHat, Moon, Clock } from 'lucide-react';
import { format } from 'date-fns';
import { Log } from '../../types';

interface SessionTrackersProps {
    ongoingFeed: Log | null;
    ongoingSleep: Log | null;
    lastCompletedFeed: Log | null;
    onStartFeed: (orientation: string) => void;
    onStopFeed: () => void;
    onStartSleep: () => void;
    onStopSleep: () => void;
}

export const SessionTrackers: React.FC<SessionTrackersProps> = ({
    ongoingFeed,
    ongoingSleep,
    lastCompletedFeed,
    onStartFeed,
    onStopFeed,
    onStartSleep,
    onStopSleep
}) => {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Feeding */}
            {ongoingFeed ? (
                <div className="bg-primary-600 text-white rounded-2xl p-6 relative overflow-hidden shadow-lg shadow-primary-200">
                    <div className="relative z-10 flex items-center justify-between">
                        <div>
                            <p className="text-primary-100 text-sm font-medium mb-1 uppercase tracking-wider">Ongoing Feed</p>
                            <h2 className="text-2xl font-bold flex items-center gap-2">
                                {ongoingFeed.orientation} Side
                            </h2>
                            <p className="text-primary-100 mt-1 flex items-center gap-2">
                                <Clock className="w-4 h-4" />
                                Started at {format(new Date(ongoingFeed.timestamp), 'HH:mm')}
                            </p>
                        </div>
                        <button
                            onClick={onStopFeed}
                            className="bg-white text-primary-600 font-bold px-6 py-3 rounded-xl shadow-lg hover:bg-primary-50 transition-all active:scale-95"
                        >
                            STOP FEED
                        </button>
                    </div>
                    <ChefHat className="absolute -right-8 -bottom-8 w-48 h-48 text-primary-500/30 rotate-12" />
                </div>
            ) : (
                <div className="card p-6 flex items-center justify-between">
                    <div>
                        <h3 className="font-bold text-lg">Feeding</h3>
                        <p className="text-sm text-slate-500">Last: {lastCompletedFeed?.duration_minutes ?? '0'}m ({lastCompletedFeed?.orientation ?? '-'})</p>
                    </div>
                    <div className="flex gap-2">
                        {['Left', 'Right', 'Expressed'].map(o => (
                            <button
                                key={o}
                                onClick={() => onStartFeed(o)}
                                className="btn btn-secondary px-3"
                            >
                                {o.charAt(0)}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Sleep */}
            {ongoingSleep ? (
                <div className="bg-indigo-600 text-white rounded-2xl p-6 relative overflow-hidden shadow-lg shadow-indigo-200">
                    <div className="relative z-10 flex items-center justify-between">
                        <div>
                            <p className="text-indigo-100 text-sm font-medium mb-1 uppercase tracking-wider">Ongoing Sleep</p>
                            <h2 className="text-2xl font-bold">Dreaming...</h2>
                            <p className="text-indigo-100 mt-1 flex items-center gap-2">
                                <Clock className="w-4 h-4" />
                                Since {format(new Date(ongoingSleep.timestamp), 'HH:mm')}
                            </p>
                        </div>
                        <button
                            onClick={onStopSleep}
                            className="bg-white text-indigo-600 font-bold px-6 py-3 rounded-xl shadow-lg hover:bg-indigo-50 transition-all active:scale-95"
                        >
                            WAKE UP
                        </button>
                    </div>
                    <Moon className="absolute -right-8 -bottom-8 w-48 h-48 text-indigo-500/30 -rotate-12" />
                </div>
            ) : (
                <div className="card p-6 flex items-center justify-between">
                    <div>
                        <h3 className="font-bold text-lg">Sleep</h3>
                        <p className="text-sm text-slate-500">Track rests and naps</p>
                    </div>
                    <button
                        onClick={onStartSleep}
                        className="btn btn-primary"
                    >
                        <Moon className="w-4 h-4" /> Start Sleep
                    </button>
                </div>
            )}
        </div>
    );
};
