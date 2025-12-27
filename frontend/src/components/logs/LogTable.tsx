import * as React from 'react';
import { format } from 'date-fns';
import { Edit, Trash2, Timer } from 'lucide-react';
import { Log } from '../../types';

interface LogTableProps {
    logs: Log[];
    onEdit: (log: Log) => void;
    onDelete: (id: number) => void;
}

const getBadgeColor = (event: string) => {
    switch (event) {
        case 'Feeding': return 'bg-orange-100 text-orange-700';
        case 'Sleep': return 'bg-indigo-100 text-indigo-700';
        case 'Pee': return 'bg-blue-100 text-blue-700';
        case 'Poop': return 'bg-emerald-100 text-emerald-700';
        case 'Mixed': return 'bg-purple-100 text-purple-700';
        default: return 'bg-slate-100 text-slate-700';
    }
};

export const LogTable: React.FC<LogTableProps> = ({ logs, onEdit, onDelete }) => {
    return (
        <div className="card shadow-md">
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-slate-50 border-b border-slate-200">
                            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Time</th>
                            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Event</th>
                            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Details</th>
                            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Orientation</th>
                            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {logs.map((log) => (
                            <tr key={log.id} className="hover:bg-slate-50/50 transition-colors">
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm font-medium">{format(new Date(log.timestamp), 'HH:mm')}</div>
                                    <div className="text-xs text-slate-400">{format(new Date(log.timestamp), 'MMM dd')}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`px-2 py-1 rounded-md text-xs font-bold ${getBadgeColor(log.event)}`}>
                                        {log.event}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-sm text-slate-600">
                                    {log.details === 'ongoing' ? (
                                        <span className="flex items-center gap-1 text-primary-600 animate-pulse">
                                            <Timer className="w-3 h-3" /> Active
                                        </span>
                                    ) : log.details}
                                </td>
                                <td className="px-6 py-4 text-sm text-slate-500">{log.orientation || '-'}</td>
                                <td className="px-6 py-4 text-sm">
                                    <div className="flex gap-3">
                                        <button
                                            onClick={() => onEdit(log)}
                                            className="text-slate-400 hover:text-primary-600 transition-colors"
                                            title="Edit Log"
                                        >
                                            <Edit className="w-4 h-4" />
                                        </button>
                                        <button
                                            onClick={() => onDelete(log.id)}
                                            className="text-slate-400 hover:text-red-500 transition-colors"
                                            title="Delete Log"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
