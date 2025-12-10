import { useQuery } from "@tanstack/react-query";
import { getSummaryStats, getDailyPostsCount, getTopSubscribers } from "../api/redditApi";

// Default query options to prevent unnecessary refetches
const defaultQueryOptions = {
    staleTime: 5 * 60 * 1000, // 5 minutes - data won't be considered stale for 5 min
    gcTime: 10 * 60 * 1000, // 10 minutes - cache persists for 10 min
    refetchOnWindowFocus: false,
    refetchOnMount: false, // Don't refetch when component remounts
    refetchOnReconnect: false,
};

export const useSummaryStats = () => {
    return useQuery({
        queryKey: ["summaryRedditStats"],
        queryFn: getSummaryStats,
        ...defaultQueryOptions
    });
};

export const useDailyPostsCount = () => {
    return useQuery({
        queryKey: ["dailyPostsCount"],
        queryFn: getDailyPostsCount,
        ...defaultQueryOptions
    });
};

export const useTopSubscribers = () => {
    return useQuery({
        queryKey: ["topSubscribers"],
        queryFn: getTopSubscribers,
        ...defaultQueryOptions
    });
};
