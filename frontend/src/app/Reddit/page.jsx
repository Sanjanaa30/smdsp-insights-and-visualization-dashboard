"use client";

import StatsCards from "../components/StatsCards";
import { MoonLoader, PropagateLoader } from "react-spinners";
import LineChart from "../components/Chart/LineChart";
import HorizontalBarChart from "../components/Chart/HorizontalBarChart";

import {
  useSummaryStats,
  useDailyPostsCount,
  useTopSubscribers,
} from "../hooks/useRedditDashboard";

export default function Page() {

  const { data: summaryRedditStats, isLoading: summaryLoading } = useSummaryStats();

  const { data: postsPerDay, isLoading: postsLoading } = useDailyPostsCount();

  const { data: topSubscribers, isLoading: topSubLoading } =
    useTopSubscribers();

  // Derived values
  const totalPosts = summaryRedditStats?.total_posts || 0;
  const totalComments = summaryRedditStats?.total_comments || 0;
  const totalToxicity = summaryRedditStats?.total_toxicity || 0;
  const numberOfSubreddit = summaryRedditStats?.unique_subreddit || 0;

  const statsConfig = [
    {
      label: "Total Posts Collected",
      value: totalPosts,
      helper: "Unique posts in dataset",
      color: "green",
      icon: "🧾",
    },
    {
      label: "Number of Comments",
      value: totalComments,
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
    <div className="container mx-auto px-10 py-5">
      {/* Summary Cards */}
      {summaryLoading ? (
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

      {/* Posts per Day Chart */}
      {postsLoading ? (
        <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white px-5 pt-5 flex items-center justify-center min-h-[400px]">
          <PropagateLoader loading={true} color="#465fff" />
        </div>
      ) : (
        <LineChart title="Daily Posts By Subreddits" data={postsPerDay} />
      )}

      {/* Top Subscribers Chart */}
      <div className="grid grid-cols-4 sm:grid-cols-1 lg:grid-cols-4 gap-4 min-h-[250px] pt-5">
        <div className="col-span-2">
          {!topSubLoading && topSubscribers?.length > 0 ? (
            <HorizontalBarChart
              title="Top Subscribers by Subreddits"
              categories={topSubscribers.map((d) => d.subreddit_name)}
              series={[
                {
                  name: "Subscribers",
                  data: topSubscribers.map((d) => d.subscribers),
                },
              ]}
            />
          ) : (
            <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white px-5 pt-5 flex items-center justify-center min-h-[250px]">
              <PropagateLoader loading={true} color="#465fff" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
