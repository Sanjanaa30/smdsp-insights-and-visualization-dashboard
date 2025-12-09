"use client";

import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  fetchSummaryStats,
  fetchDailyPostsCount,
  selectRedditDashboard,
} from "../../slices/redditSlice";
import StatsCards from "../components/StatsCards";
import { MoonLoader, SyncLoader } from "react-spinners";
import LineChart from "../components/Chart/LineChart";

export default function page() {
  const dispatch = useDispatch();
  useEffect(() => {
    dispatch(fetchSummaryStats());
    dispatch(fetchDailyPostsCount());
  }, [dispatch]);

  const { summaryStats, postsPerDay } = useSelector(selectRedditDashboard);

  const totalPosts = summaryStats?.data?.total_posts || 0;
  const totalComments = summaryStats?.data?.total_comments || 0;
  const totalToxicity = summaryStats?.data?.total_toxicity || 0;
  const numberOfSubreddit = summaryStats?.data?.unique_subreddit || 0;

  const statsConfig = [
    {
      label: "Total Posts Collected",
      value: totalPosts.toLocaleString(),
      helper: "Unique posts in dataset",
      color: "green",
      icon: "🧾",
    },
    {
      label: "Number of Comments",
      value: totalComments.toLocaleString(),
      helper: "Unique comments in dataset",
      color: "purple",
      icon: "💬",
    },
    {
      label: "Total Numbers Records Scored Toxicity",
      value: totalToxicity,
      helper: "Scored Toxicity Using Perspective API",
      color: "orange",
      icon: "⚠️",
    },
    {
      label: "Number of Subreddit",
      value: numberOfSubreddit,
      helper: "Unique Subreddit in dataset",
      color: "blue",
      icon: "📊",
    },
  ];

  return (
    <div className="container mx-auto p-2">
      {summaryStats.loading ? (
        <div className="grid grid-cols-3 gap-4 mb-4">
          {Array.from({ length: statsConfig.length }).map((_, i) => (
            <div
              key={i}
              className="overflow-hidden rounded-2xl border border-gray-200 bg-white px-5 py-8 
                      flex items-center justify-center"
            >
              <MoonLoader color="#465fff" size={12} />
            </div>
          ))}
        </div>
      ) : (
        <StatsCards items={statsConfig} />
      )}
      <LineChart
        title="Daily Posts By Subreddits"
        data={postsPerDay?.data}
        // onApplyFilters={}
        // filterLabel={boardOptions.map((opt) => opt.label)}
        // defaultFilter={
        //   boardOptions.find((opt) => opt.value === selectedBoard)?.label ||
        //   "All Boards"
        // }
      />
    </div>
  );
}
