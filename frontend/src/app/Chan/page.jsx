"use client";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { MoonLoader, SyncLoader } from "react-spinners";
import {
  fetchStatsDaily,
  fetchSummaryStats,
  fetchCountryStats,
  selectPostsPerDay,
  selectSummaryStats,
  selectCountryStats,
} from "../../slices/chanSlice";
import BarChart from "../components/Chart/BarChart";
import StatsCards from "../components/StatsCards";
import CountriesCard from "../components/CountriesCard/CountriesCard";

export default function page() {
  const dispatch = useDispatch();
  const postsPerDay = useSelector(selectPostsPerDay);
  const summaryStats = useSelector(selectSummaryStats);
  const countryStats = useSelector(selectCountryStats);
  // Filter states
  const [selectedBoard, setSelectedBoard] = useState("");
  const [startDate, setStartDate] = useState("2025-11-15");
  const [endDate, setEndDate] = useState("");
  // Board options
  const boardOptions = [
    { value: "", label: "All Boards" },
    { value: "pol", label: "Politically Incorrect" },
    { value: "int", label: "International" },
    { value: "g", label: "Technology" },
    { value: "sp", label: "Sports" },
    { value: "out", label: "Outdoor" },
  ];

  useEffect(() => {
    handleApplyFilters();
  }, []);
  const handleApplyFilters = () => {
    const params = {};
    if (selectedBoard) params.board_name = selectedBoard;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    dispatch(fetchStatsDaily(params));
    dispatch(fetchSummaryStats());
    dispatch(fetchCountryStats(params));
  };

  // Handler for BarChart filter changes
  const handleChartFilters = ({
    category,
    startDate: newStartDate,
    endDate: newEndDate,
  }) => {
    // Update local state
    if (newStartDate !== undefined) setStartDate(newStartDate);
    if (newEndDate !== undefined) setEndDate(newEndDate);

    // Handle board selection from category
    if (category !== undefined) {
      const selectedOption = boardOptions.find((opt) => opt.label === category);
      if (selectedOption) {
        setSelectedBoard(selectedOption.value);
      }
    }

    // Build params for API call
    const params = {};
    const boardValue =
      category !== undefined
        ? boardOptions.find((opt) => opt.label === category)?.value || ""
        : selectedBoard;

    if (boardValue) params.board_name = boardValue;
    if (newStartDate) params.start_date = newStartDate;
    if (newEndDate) params.end_date = newEndDate;

    // Fetch updated data
    dispatch(fetchStatsDaily(params));
  };

  const data = postsPerDay?.data || [];
  const totalPosts = summaryStats?.data?.total_posts || 0;
  const totalToxicity = summaryStats?.data?.total_toxicity || 0;
  const numberOfBoards = summaryStats?.data?.unique_boards || 0;
  // ----- CONFIG FOR THE REUSABLE STATS CARDS -----
  const statsConfig = [
    {
      label: "Total Posts Collected",
      value: totalPosts.toLocaleString(),
      // helper: "Within selected filters",
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
  console.log(postsPerDay?.data);

  // Countries Card Data - Use real data from API
  const [range, setRange] = useState("Last 7 Days");

  const countryList = countryStats?.data?.data || [];

  const countryStatsForCard = countryList.map((country) => ({
    name: country.name,
    percent: country.percent,
    flag: country.flag,
  }));

  const mapData = countryList.reduce((acc, country) => {
    acc[country.name] = country.percent;
    return acc;
  }, {});

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
      {/* Chart Display */}
      <div className="grid grid-cols-4 sm:grid-cols-1 lg:grid-cols-4 gap-4 min-h-[250px]">
        {/* Daily Posts Chart Section */}
        <div className="col-span-3">
          {postsPerDay.loading ? (
            <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white px-5 pt-5 sm:px-6 sm:pt-6 flex items-center justify-center">
              <SyncLoader loading={true} color="#465fff" size={26} />
            </div>
          ) : (
            <BarChart
              title="Daily Posts"
              data={postsPerDay?.data}
              onApplyFilters={handleChartFilters}
              filterLabel={boardOptions.map((opt) => opt.label)}
              defaultFilter={
                boardOptions.find((opt) => opt.value === selectedBoard)
                  ?.label || "All Boards"
              }
            />
          )}
        </div>

        {/* Countries Card Section */}
        <div className="col-span-1">
          {countryStats.loading ? (
            <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white px-5 pt-5 sm:px-6 sm:pt-6 flex items-center justify-center min-h-[400px]">
              <SyncLoader loading={true} color="#465fff" />
            </div>
          ) : (
            <CountriesCard
              countryStats={countryStatsForCard}
              range={range}
              mapData={mapData}
            />
          )}
        </div>
      </div>

      {/* <div className="grid grid-cols-2 gap-4 min-h-[250px]">
       </div> */}
    </div>
  );
}
