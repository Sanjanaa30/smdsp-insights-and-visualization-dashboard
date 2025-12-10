"use client";

import { useState } from "react";
import {
  useDailyStats,
  useSummaryStats,
  useCountryStats,
  useEngagementByType,
} from "../hooks/useChanDashboard";

import { MoonLoader, SyncLoader } from "react-spinners";

import BarChart from "../components/Chart/BarChart";
import StatsCards from "../components/StatsCards";
import CountriesCard from "../components/CountriesCard/CountriesCard";
import GroupedBarChart from "../components/Chart/GroupedBarChart";

export default function Page() {
  // ---------------- FILTER STATE FOR DAILY STATS ----------------
  const [dailyBoard, setDailyBoard] = useState("pol");
  const [dailyStartDate, setDailyStartDate] = useState("2025-11-14");
  const [dailyEndDate, setDailyEndDate] = useState("2025-12-05");

  // ---------------- FILTER STATE FOR ENGAGEMENT ----------------
  const [engagementBoard, setEngagementBoard] = useState("pol");
  const [engagementStartDate, setEngagementStartDate] = useState("2025-11-14");
  const [engagementEndDate, setEngagementEndDate] = useState("2025-12-05");

  const boardOptions = [
    { value: "", label: "All Boards" },
    { value: "pol", label: "Politically Incorrect" },
    { value: "int", label: "International" },
    { value: "g", label: "Technology" },
    { value: "sp", label: "Sports" },
    { value: "out", label: "Outdoor" },
  ];

  // ---------------- REACT QUERY CALLS ----------------

  const { data: postsPerDay, isLoading: loadingDaily } = useDailyStats({
    board_name: dailyBoard,
    start_date: dailyStartDate,
    end_date: dailyEndDate,
  });

  const { data: summaryChanStats, isLoading: loadingSummary } = useSummaryStats();

  const { data: countryStats, isLoading: loadingCountry } = useCountryStats();

  const { data: engagementStats, isLoading: loadingEngagement } =
    useEngagementByType({
      board_name: engagementBoard,
      start_date: engagementStartDate,
      end_date: engagementEndDate,
    });

  // ---------------- HANDLE FILTER CHANGES FOR DAILY STATS ----------------
  const handleDailyFilters = ({
    category,
    startDate: newStartDate,
    endDate: newEndDate,
  }) => {
    if (newStartDate !== undefined) setDailyStartDate(newStartDate);
    if (newEndDate !== undefined) setDailyEndDate(newEndDate);

    if (category !== undefined) {
      const option = boardOptions.find((x) => x.label === category);
      if (option) setDailyBoard(option.value);
    }
  };

  // ---------------- HANDLE FILTER CHANGES FOR ENGAGEMENT ----------------
  const handleEngagementFilters = ({
    category,
    startDate: newStartDate,
    endDate: newEndDate,
  }) => {
    if (newStartDate !== undefined) setEngagementStartDate(newStartDate);
    if (newEndDate !== undefined) setEngagementEndDate(newEndDate);

    if (category !== undefined) {
      const option = boardOptions.find((x) => x.label === category);
      if (option) setEngagementBoard(option.value);
    }
  };

  // ---------------- SUMMARY CARDS ----------------

  const totalPosts = summaryChanStats?.total_posts || 0;
  const totalToxicity = summaryChanStats?.total_toxicity || 0;
  const numberOfBoards = summaryChanStats?.unique_boards || 0;

  const statsConfig = [
    {
      label: "Total Posts Collected",
      value: totalPosts,
      color: "green",
      icon: "🧾",
    },
    {
      label: "Scored Toxicity Data",
      value: totalToxicity,
      helper: "Total Numbers Records Scored Toxicity",
      color: "orange",
      icon: "⚠️",
    },
    {
      label: "Number of Boards",
      value: numberOfBoards,
      helper: "Unique boards in dataset",
      color: "blue",
      icon: "📊",
    },
  ];

  // ---------------- COUNTRY DATA ----------------

  const countryList = countryStats?.data || [];

  const countryStatsForCard = countryList.map((c) => ({
    name: c.name,
    percent: c.percent,
    flag: c.flag,
  }));

  const mapData = Object.fromEntries(
    countryList.map((c) => [c.name, c.percent])
  );

  // ---------------- RENDER UI ----------------

  return (
    <div className="container mx-auto p-2">
      {/* ---------- SUMMARY CARDS ---------- */}
      {loadingSummary ? (
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

      {/* ---------- MAIN GRID ---------- */}
      <div className="grid grid-cols-4 md:grid-cols-4 gap-4">
        {/* ---------- DAILY POSTS ---------- */}
        <div className="col-span-3">
          <div className="col-span-2 my-1">
            {loadingDaily ? (
              <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white px-5 pt-5 flex items-center justify-center min-h-[300px]">
                <SyncLoader color="#465fff" size={26} />
              </div>
            ) : (
              <BarChart
                title="Daily Posts"
                data={postsPerDay}
                onFilterChange={handleDailyFilters}
                filterLabel={boardOptions.map((opt) => opt.label)}
                defaultFilter={
                  boardOptions.find((opt) => opt.value === dailyBoard)?.label
                }
                showDateFilter={true}
                showDropdown={true}
                startDate={dailyStartDate}
                endDate={dailyEndDate}
                minDate="2025-11-01"
              />
            )}
          </div>
          <div className="col-span-2 my-1">
            {/* ---------- ENGAGEMENT CHART (FULL WIDTH) ---------- */}
            <div className="mt-4">
              {loadingEngagement ? (
                <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white px-5 pt-5 flex items-center justify-center min-h-[400px]">
                  <SyncLoader color="#465fff" />
                </div>
              ) : (
                <GroupedBarChart
                  title="Engagement by Post Type"
                  data={engagementStats}
                  onFilterChange={handleEngagementFilters}
                  filterLabel={boardOptions.map((opt) => opt.label)}
                  defaultFilter={
                    boardOptions.find((opt) => opt.value === engagementBoard)?.label
                  }
                  showDateFilter={true}
                  showDropdown={true}
                  startDate={engagementStartDate}
                  endDate={engagementEndDate}
                  minDate="2025-11-01"
                />
              )}
            </div>
          </div>
        </div>

        {/* ---------- COUNTRY STATS ---------- */}
        <div className="col-span-1 my-1">
          {loadingCountry ? (
            <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white px-5 pt-5 flex items-center justify-center min-h-[400px]">
              <SyncLoader color="#465fff" />
            </div>
          ) : (
            <CountriesCard
              countryStats={countryStatsForCard}
              mapData={mapData}
            />
          )}
        </div>
      </div>
    </div>
  );
}
