import { useQuery } from "@tanstack/react-query";
import { getToxicity } from "../api/comparisonApi";

// Default query options to prevent unnecessary refetches
const defaultQueryOptions = {
    staleTime: 5 * 60 * 1000, // 5 minutes - data won't be considered stale for 5 min
    gcTime: 10 * 60 * 1000, // 10 minutes - cache persists for 10 min
    refetchOnWindowFocus: false,
    refetchOnMount: false, // Don't refetch when component remounts
    refetchOnReconnect: false,
};

export const useToxicity = ({ board_name, start_date, end_date } = {}) => {
    return useQuery({
        queryKey: ["toxicity", board_name, start_date, end_date],
        queryFn: () => getToxicity({ board_name, start_date, end_date }),
        enabled: true, // always fetch on mount. Set to false if you want manual trigger.
        ...defaultQueryOptions
    });
};
