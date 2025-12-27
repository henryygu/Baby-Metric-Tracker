import { useState, useEffect, useCallback } from 'react';
import { logService } from '../api/logService';
import { DashboardData, Log, BabyConfig } from '../types';

export const useDashboardData = () => {
    const [data, setData] = useState<DashboardData | null>(null);
    const [logs, setLogs] = useState<Log[]>([]);
    const [config, setConfig] = useState<BabyConfig | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchData = useCallback(async () => {
        try {
            const [dashResp, logsResp, configResp] = await Promise.all([
                logService.getDashboard(),
                logService.getLogs(),
                logService.getConfig()
            ]);
            setData(dashResp.data);
            setLogs(logsResp.data);
            setConfig(configResp.data);
        } catch (error) {
            console.error('Error fetching data:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, [fetchData]);

    const logEvent = async (event: string, extra: any = {}) => {
        await logService.logEvent(event, extra);
        fetchData();
    };

    const updateLog = async (id: number, logData: Partial<Log>) => {
        await logService.updateLog(id, logData);
        fetchData();
    };

    const stopSession = async (type: string) => {
        await logService.stopSession(type);
        fetchData();
    };

    const deleteLog = async (id: number) => {
        if (!confirm('Are you sure you want to delete this log?')) return;
        await logService.deleteLog(id);
        fetchData();
    };

    return {
        data,
        logs,
        config,
        loading,
        fetchData,
        logEvent,
        updateLog,
        stopSession,
        deleteLog
    };
};
