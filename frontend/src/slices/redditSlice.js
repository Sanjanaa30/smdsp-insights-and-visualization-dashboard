import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { createSelector } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/reddit/';

// Async thunk to fetch summary stats
export const fetchSummaryStats = createAsyncThunk(
    'redditDashboard/fetchSummaryStats',
    async ({ } = {}, { rejectWithValue }) => {
        try {

            const response = await axios.get(API_URL + "stats/summary");
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response?.data || error.message);
        }
    }
);

// Async thunk to fetch summary stats
export const fetchDailyPostsCount = createAsyncThunk(
    'redditDashboard/fetchDailyPostsCount',
    async ({ } = {}, { rejectWithValue }) => {
        try {

            const response = await axios.get(API_URL + "posts/daily-counts");
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response?.data || error.message);
        }
    }
);

const redditDashboardSlice = createSlice({
    name: 'redditDashboard',
    initialState: {
        postsPerDay: { data: null, loading: false, error: null },
        summaryStats: { data: null, loading: false, error: null },
        countryStats: { data: null, loading: false, error: null },
        // You can add other states here if needed (e.g., users, revenue)
    },

    reducers: {},

    extraReducers: (builder) => {
        builder
            .addCase(fetchSummaryStats.pending, (state) => {
                state.summaryStats.loading = true;
                state.summaryStats.error = null;
            })
            .addCase(fetchSummaryStats.fulfilled, (state, action) => {
                state.summaryStats.loading = false;
                state.summaryStats.data = action.payload;
            })
            .addCase(fetchSummaryStats.rejected, (state, action) => {
                state.summaryStats.loading = false;
                state.summaryStats.error = action.payload || 'Failed to fetch summary stats';
            })
            .addCase(fetchDailyPostsCount.pending, (state) => {
                state.postsPerDay.loading = true;
                state.postsPerDay.error = null;
            })
            .addCase(fetchDailyPostsCount.fulfilled, (state, action) => {
                state.postsPerDay.loading = false;
                state.postsPerDay.data = action.payload;
            })
            .addCase(fetchDailyPostsCount.rejected, (state, action) => {
                state.postsPerDay.loading = false;
                state.postsPerDay.error = action.payload || 'Failed to fetch posts per day count';
            })
    }
})

// Memoized selectors to prevent unnecessary rerenders
export const selectSummaryStats = (state) => state.redditDashboard.summaryStats;
export const selectPostsPerDay = (state) => state.redditDashboard.postsPerDay;

export const selectRedditDashboard = createSelector(
    [selectSummaryStats, selectPostsPerDay],
    (summaryStats, postsPerDay) => ({
        summaryStats,
        postsPerDay,
    })
);

export default redditDashboardSlice.reducer;