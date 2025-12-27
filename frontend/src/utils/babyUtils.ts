import { differenceInDays } from 'date-fns';
import { BabyConfig } from '../types';

export type AgeFormat = 'days' | 'months' | 'years' | 'complex';

export const formatAge = (config: BabyConfig | null, format: AgeFormat) => {
    if (!config) return '';
    const days = differenceInDays(new Date(), new Date(config.date_of_birth));

    switch (format) {
        case 'days': return `${days} days old`;
        case 'months': return `${(days / 30.41).toFixed(1)} months old`;
        case 'years': return `${(days / 365.25).toFixed(2)} years old`;
        case 'complex': {
            const y = Math.floor(days / 365.25);
            const m = Math.floor((days % 365.25) / 30.41);
            const d = Math.floor((days % 30.41));
            return `${y}y ${m}m ${d}d`;
        }
    }
};
