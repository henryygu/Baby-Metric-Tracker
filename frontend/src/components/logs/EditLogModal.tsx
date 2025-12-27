import * as React from 'react';
import { useRef } from 'react';
import { Log } from '../../types';

interface EditLogModalProps {
    log: Log;
    onClose: () => void;
    onSave: (id: number, data: Partial<Log>) => void;
}

export const EditLogModal: React.FC<EditLogModalProps> = ({ log, onClose, onSave }) => {
    const detailsRef = useRef<HTMLInputElement>(null);
    const orientationRef = useRef<HTMLSelectElement>(null);
    const commentsRef = useRef<HTMLTextAreaElement>(null);
    const weightRef = useRef<HTMLInputElement>(null);
    const heightRef = useRef<HTMLInputElement>(null);

    const handleSave = () => {
        const data: Partial<Log> = {
            details: detailsRef.current?.value || '',
            orientation: orientationRef.current?.value || '',
            comments: commentsRef.current?.value || '',
        };

        if (log.event === 'Growth') {
            data.weight = weightRef.current?.value ? parseFloat(weightRef.current.value) : undefined;
            data.height = heightRef.current?.value ? parseFloat(heightRef.current.value) : undefined;
        }

        onSave(log.id, data);
    };

    return (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-2xl">
                <h3 className="text-xl font-bold mb-6">Edit {log.event} Log</h3>
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Details / Duration</label>
                        <input
                            type="text"
                            defaultValue={log.details || ''}
                            ref={detailsRef}
                            className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:ring-2 focus:ring-primary-500 outline-none"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Orientation</label>
                        <select
                            defaultValue={log.orientation || ''}
                            ref={orientationRef}
                            className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:ring-2 focus:ring-primary-500 outline-none"
                        >
                            <option value="">None</option>
                            <option value="Left">Left</option>
                            <option value="Right">Right</option>
                            <option value="Expressed">Expressed</option>
                            <option value="Mum">Mum</option>
                            <option value="Dad">Dad</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Comments</label>
                        <textarea
                            defaultValue={log.comments || ''}
                            ref={commentsRef}
                            className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:ring-2 focus:ring-primary-500 outline-none h-24"
                        ></textarea>
                    </div>
                    {log.event === 'Growth' && (
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Weight (kg)</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    defaultValue={log.weight || ''}
                                    ref={weightRef}
                                    className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:ring-2 focus:ring-primary-500 outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Height (cm)</label>
                                <input
                                    type="number"
                                    step="0.1"
                                    defaultValue={log.height || ''}
                                    ref={heightRef}
                                    className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:ring-2 focus:ring-primary-500 outline-none"
                                />
                            </div>
                        </div>
                    )}
                </div>
                <div className="flex gap-3 mt-8">
                    <button
                        onClick={onClose}
                        className="flex-1 px-4 py-2 rounded-lg font-bold text-slate-600 hover:bg-slate-50 border border-slate-200"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSave}
                        className="flex-1 px-4 py-2 rounded-lg font-bold bg-primary-600 text-white hover:bg-primary-700 shadow-lg shadow-primary-200"
                    >
                        Save Changes
                    </button>
                </div>
            </div>
        </div>
    );
};
