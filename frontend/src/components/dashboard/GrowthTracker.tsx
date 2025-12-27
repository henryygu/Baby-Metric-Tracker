import * as React from 'react';
import { useRef } from 'react';
import { Baby } from 'lucide-react';

interface GrowthTrackerProps {
    onRecord: (weight: number | null, height: number | null) => void;
}

export const GrowthTracker: React.FC<GrowthTrackerProps> = ({ onRecord }) => {
    const weightRef = useRef<HTMLInputElement>(null);
    const heightRef = useRef<HTMLInputElement>(null);

    const handleRecord = () => {
        const w = weightRef.current?.value;
        const h = heightRef.current?.value;
        if (w || h) {
            onRecord(w ? parseFloat(w) : null, h ? parseFloat(h) : null);
            if (weightRef.current) weightRef.current.value = '';
            if (heightRef.current) heightRef.current.value = '';
        }
    };

    return (
        <div className="card p-6 bg-white border-slate-200">
            <h3 className="font-bold mb-4 flex items-center gap-2 text-slate-800">
                <Baby className="w-5 h-5 text-indigo-600" />
                Growth Tracking
            </h3>
            <div className="space-y-3">
                <div className="flex gap-2">
                    <input
                        ref={weightRef}
                        type="number"
                        step="0.01"
                        placeholder="Weight (kg)"
                        className="w-1/2 px-3 py-2 rounded-lg border border-slate-200 text-sm focus:ring-2 focus:ring-primary-500 outline-none"
                    />
                    <input
                        ref={heightRef}
                        type="number"
                        step="0.1"
                        placeholder="Height (cm)"
                        className="w-1/2 px-3 py-2 rounded-lg border border-slate-200 text-sm focus:ring-2 focus:ring-primary-500 outline-none"
                    />
                </div>
                <button
                    onClick={handleRecord}
                    className="w-full py-2 bg-indigo-600 text-white rounded-lg text-sm font-bold hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-100"
                >
                    Record Measurement
                </button>
            </div>
        </div>
    );
};
