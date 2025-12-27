import * as React from 'react';
import { Droplets } from 'lucide-react';

interface DiaperQuickLogProps {
    onLog: (type: string, extra: any) => void;
}

export const DiaperQuickLog: React.FC<DiaperQuickLogProps> = ({ onLog }) => {
    return (
        <div className="lg:col-span-2 card p-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="font-bold flex items-center gap-2">
                    <Droplets className="w-5 h-5 text-primary-600" />
                    Quick Diaper Log
                </h3>
            </div>
            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-4">
                    <p className="text-sm font-medium text-slate-500">MUM</p>
                    <div className="flex flex-wrap gap-2">
                        <button onClick={() => onLog('Pee', { orientation: 'Mum' })} className="btn btn-secondary flex-1">Pee</button>
                        <button onClick={() => onLog('Poop', { orientation: 'Mum' })} className="btn btn-secondary flex-1">Poop</button>
                        <button onClick={() => onLog('Mixed', { orientation: 'Mum' })} className="btn btn-secondary w-full">Mixed</button>
                    </div>
                </div>
                <div className="space-y-4">
                    <p className="text-sm font-medium text-slate-500">DAD</p>
                    <div className="flex flex-wrap gap-2">
                        <button onClick={() => onLog('Pee', { orientation: 'Dad' })} className="btn btn-secondary flex-1">Pee</button>
                        <button onClick={() => onLog('Poop', { orientation: 'Dad' })} className="btn btn-secondary flex-1">Poop</button>
                        <button onClick={() => onLog('Mixed', { orientation: 'Dad' })} className="btn btn-secondary w-full">Mixed</button>
                    </div>
                </div>
            </div>
        </div>
    );
};
