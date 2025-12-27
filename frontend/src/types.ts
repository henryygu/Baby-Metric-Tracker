export interface Log {
    id: number;
    event: string;
    details: string;
    timestamp: string;
    comments?: string;
    end_timestamp?: string;
    orientation?: string;
    feed_id?: number;
    duration_minutes?: number;
    weight?: number;
    height?: number;
}

export interface DailyStats {
    today_count: number;
    yesterday_count: number;
    delta: number;
}

export interface FeedStats {
    today_count: number;
    today_duration: number;
    today_avg: number;
    yesterday_count: number;
    yesterday_duration: number;
    yesterday_avg: number;
    count_delta: number;
    duration_delta: number;
    avg_delta: number;
}

export interface DiaperStats {
    pee: DailyStats;
    poop: DailyStats;
    mixed: DailyStats;
    total: DailyStats;
    last_type: string | null;
    last_time_str: string | null;
    last_pee_str?: string | null;
    last_poop_str?: string | null;
}

export interface HistoryData {
    feeding: { date: string, count: number, details: any }[];
    diaper: { date: string, count: number, details: any }[];
    sleep: { date: string, total_hours: number }[];
    growth: { date: string, weight?: number, height?: number }[];
}

export interface DashboardData {
    feeding: FeedStats;
    diapers: DiaperStats;
    ongoing_feed: Log | null;
    ongoing_sleep: Log | null;
    last_completed_feed: Log | null;
    predictions?: {
        sleep: {
            past: any[];
            future: any[];
            summary?: {
                stage: string;
                nap_count: number;
                total_hours: number;
                details: Array<{
                    start: string;
                    end: string;
                    duration: number;
                    type: string;
                }>;
            };
        }
    };
    history?: HistoryData;
}

export interface BabyConfig {
    name: string;
    date_of_birth: string;
}
