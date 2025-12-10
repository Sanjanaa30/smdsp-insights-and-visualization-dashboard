import { useQuery } from "@tanstack/react-query";
import {
    getDailyStats,
    getSummaryStats,
    getCountryStats,
    getEngagementByType,
} from "../api/chanApi";

// Default query options to prevent unnecessary refetches
const defaultQueryOptions = {
    staleTime: 5 * 60 * 1000, // 5 minutes - data won't be considered stale for 5 min
    gcTime: 10 * 60 * 1000, // 10 minutes - cache persists for 10 min
    refetchOnWindowFocus: false,
    refetchOnMount: false, // Don't refetch when component remounts
    refetchOnReconnect: false,
};

// Daily Posts
export const useDailyStats = ({ board_name, start_date, end_date }) =>
    useQuery({
        queryKey: ["dailyStats", board_name, start_date, end_date],
        queryFn: () => getDailyStats({ board_name, start_date, end_date }),
        ...defaultQueryOptions,
    });

// Summary Stats
export const useSummaryStats = () =>
    useQuery({
        queryKey: ["summaryChanStats"],
        queryFn: getSummaryStats,
        ...defaultQueryOptions,
    });

// Country Stats
export const useCountryStats = () =>
    useQuery({
        queryKey: ["countryStats"],
        queryFn: getCountryStats,
        ...defaultQueryOptions,
    });

// Engagement by Type
export const useEngagementByType = ({ board_name, start_date, end_date }) =>
    useQuery({
        queryKey: ["engagementByType", board_name, start_date, end_date],
        queryFn: () => getEngagementByType({ board_name, start_date, end_date }),
        ...defaultQueryOptions,
    });
