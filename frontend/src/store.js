import { configureStore } from '@reduxjs/toolkit';
import chanDashboardReducer from './slices/chanSlice';
import redditDashboardReducer from './slices/redditSlice';

const store = configureStore({
  reducer: {
    chanDashboard: chanDashboardReducer,
    redditDashboard: redditDashboardReducer,
  },
});

export default store;
