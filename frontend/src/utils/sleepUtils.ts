import { format } from 'date-fns';

export const transformSleepData = (past: any[], future: any[]) => {
    // Group by date
    const byDate: Record<string, any[]> = {};
    const all = [...past, ...future];

    all.forEach(s => {
        const d = format(new Date(s.date), 'MM/dd');
        if (!byDate[d]) byDate[d] = [];
        byDate[d].push(s);
    });

    const result: any[] = [];
    Object.entries(byDate).forEach(([date, sleeps]) => {
        // Sort sleeps by start time
        sleeps.sort((a, b) => a.start.localeCompare(b.start));

        const entry: any = { date };
        let lastEnd = 0;
        sleeps.forEach((s, i) => {
            const startParts = s.start.split(':').map(Number);
            const endParts = s.end.split(':').map(Number);
            const startMin = startParts[0] * 60 + startParts[1];
            let endMin = endParts[0] * 60 + endParts[1];
            if (endMin < startMin) endMin += 1440;

            entry[`gap_${i}`] = startMin - lastEnd;
            entry[`sleep_${i}`] = endMin - startMin;
            entry[`is_predicted_${i}`] = s.is_predicted;
            entry[`label_${i}`] = `${s.start} - ${s.end}`;
            lastEnd = endMin;
        });
        result.push(entry);
    });

    return result;
};
