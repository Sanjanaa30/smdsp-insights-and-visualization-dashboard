"use client";

import { SyncLoader } from "react-spinners";
import BarChart from "../components/Chart/BarChart";
import { useState } from "react";
import { useToxicity } from "../hooks/useComparisonDashboard";

export default function ComparisonPage() {
  const [selectedPlatform, setSelectedPlatform] = useState("all");

  // Fetch toxicity data with React Query
  const { data: toxicityData, isLoading, error } = useToxicity();

  if (error) {
    return (
      <div className="text-center text-red-600 py-10">
        Failed to load toxicity data.
      </div>
    );
  }

  // Filter based on selected platform
  const filteredData =
    toxicityData?.filter((item) =>
      selectedPlatform === "all" ? true : item.platform === selectedPlatform
    ) || [];

  // Format for BarChart
  const chartData = filteredData.map((item) => ({
    day: `${item.forum_name} (${item.platform})`,
    count: item.average_toxicity,
  }));

  const platformOptions = [
    { value: "all", label: "All Platforms" },
    { value: "4chan", label: "4chan" },
    { value: "reddit", label: "Reddit" },
  ];

  return (
    <div className="container mx-auto p-2">
      <div className="col-span-3">
        {isLoading ? (
          <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white px-5 pt-5 sm:px-6 sm:pt-6 flex items-center justify-center min-h-[300px]">
            <SyncLoader loading={true} color="#465fff" size={26} />
          </div>
        ) : (
          <BarChart
            title="Average Toxicity Per Boards/Subreddit (4chan & Reddit)"
            data={chartData}
            filterLabel={platformOptions.map((opt) => opt.label)}
            defaultFilter={
              platformOptions.find((opt) => opt.value === selectedPlatform)
                ?.label || "All Platforms"
            }
            onFilterChange={({ category }) => {
              const selected = platformOptions.find(
                (opt) => opt.label === category
              );
              if (selected) {
                setSelectedPlatform(selected.value);
              }
            }}
          />
        )}
      </div>
    </div>
  );
}
