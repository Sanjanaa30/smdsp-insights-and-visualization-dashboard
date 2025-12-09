import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { createSelector } from '@reduxjs/toolkit';
import axios from 'axios';

// Your full API URL
const API_URL = 'http://127.0.0.1:8000/chan/';

// Async thunk to fetch daily stats using axios GET
export const fetchStatsDaily = createAsyncThunk(
    'chanDashboard/fetchStatsDaily',  // use unique action name
    async ({ board_name, start_date, end_date } = {}, { rejectWithValue }) => {
        try {
            const params = {};
            if (board_name) params.board_name = board_name;
            if (start_date) params.start_date = start_date;
            if (end_date) params.end_date = end_date;
            
            const response = await axios.get(API_URL + "stats/daily", { params });
            return response.data;  // axios puts data in response.data
        } catch (error) {
            // Return a rejected value to be caught in rejected reducer
            return rejectWithValue(error.response?.data || error.message);
        }
    }
);

// Async thunk to fetch summary stats
export const fetchSummaryStats = createAsyncThunk(
    'chanDashboard/fetchSummaryStats',
    async ({} = {}, { rejectWithValue }) => {
        try {
                     
            const response = await axios.get(API_URL + "stats/summary");
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response?.data || error.message);
        }
    }
);

// Async thunk to fetch country stats
export const fetchCountryStats = createAsyncThunk(
    'chanDashboard/fetchCountryStats',
    async ({ board_name, start_date, end_date } = {}, { rejectWithValue }) => {
        try {
            const params = {};
            if (board_name) params.board_name = board_name;
            if (start_date) params.start_date = start_date;
            if (end_date) params.end_date = end_date;
            
            const response = await axios.get(API_URL + "stats/countries", { params });
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response?.data || error.message);
        }
    }
);

const chanDashboardSlice = createSlice({
    name: 'chanDashboard',
    initialState: {
        postsPerDay: { data: null, loading: false, error: null },
        summaryStats: { data: null, loading: false, error: null },
        countryStats: { data: null, loading: false, error: null },
        // You can add other states here if needed (e.g., users, revenue)
    },

    reducers: {},

    extraReducers: (builder) => {
        builder
            .addCase(fetchStatsDaily.pending, (state) => {
                state.postsPerDay.loading = true;
                state.postsPerDay.error = null;
            })
            .addCase(fetchStatsDaily.fulfilled, (state, action) => {
                state.postsPerDay.loading = false;
                state.postsPerDay.data = action.payload;
            })
            .addCase(fetchStatsDaily.rejected, (state, action) => {
                state.postsPerDay.loading = false;
                state.postsPerDay.error = action.payload || 'Failed to fetch posts per day data';
            })
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
            .addCase(fetchCountryStats.pending, (state) => {
                state.countryStats.loading = true;
                state.countryStats.error = null;
            })
            .addCase(fetchCountryStats.fulfilled, (state, action) => {
                state.countryStats.loading = false;
                state.countryStats.data = action.payload;
            })
            .addCase(fetchCountryStats.rejected, (state, action) => {
                state.countryStats.loading = false;
                state.countryStats.error = action.payload || 'Failed to fetch country stats';
            });
    },
});

// Memoized selectors to prevent unnecessary rerenders
export const selectPostsPerDay = (state) => state.chanDashboard.postsPerDay;
export const selectSummaryStats = (state) => state.chanDashboard.summaryStats;
export const selectCountryStats = (state) => state.chanDashboard.countryStats;

export const selectChanDashboard = createSelector(
    [selectPostsPerDay, selectSummaryStats, selectCountryStats],
    (postsPerDay, summaryStats, countryStats) => ({
        postsPerDay,
        summaryStats,
        countryStats,
    })
);

export default chanDashboardSlice.reducer;