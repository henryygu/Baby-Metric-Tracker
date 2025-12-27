import apiClient from './apiClient';
import { DashboardData, Log, BabyConfig } from '../types';

export const logService = {
    getDashboard: () => apiClient.get<DashboardData>('/dashboard'),
    getLogs: (limit = 100) => apiClient.get<Log[]>(`/logs?limit=${limit}`),
    getConfig: () => apiClient.get<BabyConfig>('/config'),

    logEvent: (event: string, extra: any = {}) =>
        apiClient.post('/logs', { event, ...extra }),

    updateLog: (id: number, logData: Partial<Log>) =>
        apiClient.put<Log>(`/logs/${id}`, logData),

    deleteLog: (id: number) =>
        apiClient.delete(`/logs/${id}`),

    stopSession: (type: string) =>
        apiClient.post(`/logs/${type}/stop`),
};
