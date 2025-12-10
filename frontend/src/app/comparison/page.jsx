"use client";

import { PropagateLoader, SyncLoader } from "react-spinners";
import BarChart from "../components/Chart/BarChart";
import LineChart from "../components/Chart/LineChart";
import { useState } from "react";
import { useToxicity, useEventRelated } from "../hooks/useComparisonDashboard";

// Community options by platform
const CHAN_COMMUNITIES = [
  { value: "g", label: "Technology" },
  { value: "pol", label: "Politics" },
  { value: "int", label: "International" },
  { value: "sp", label: "Sport" },
];

const REDDIT_COMMUNITIES = [
  { value: "technology", label: "Technology" },
  { value: "ArtificialInteligence", label: "Artificial Inteligence" },
  { value: "geopolitics", label: "Geopolitics" },
  { value: "autogpt", label: "Autogpt" },
];

const WINDOW_OPTIONS = [
  { value: 3, label: "3 days" },
  { value: 7, label: "7 days" },
  { value: 14, label: "14 days" },
  { value: 30, label: "30 days" },
];

const PLATFORM_OPTIONS = [
  { value: "all", label: "Total" },
  { value: "chan", label: "4chan" },
  { value: "reddit", label: "Reddit" },
];

export default function ComparisonPage() {
  const [selectedPlatform, setSelectedPlatform] = useState("all");

  // Event timeline filters
  const [platform, setPlatform] = useState("chan");
  const [community, setCommunity] = useState("g");
  const [windowSize, setWindowSize] = useState(7);
  const eventDate = "2025-11-18"; // Fixed event date for Cloudflare outage

  // Fetch toxicity data with React Query
  const { data: toxicityData, isLoading, error } = useToxicity();

  const {
    data: eventRelatedData,
    isLoading: eventLoading,
    error: eventError,
  } = useEventRelated({ platform, community, eventDate, window: windowSize });

  // Get community options based on selected platform
  const getCommunityOptions = () => {
    if (platform === "chan") return CHAN_COMMUNITIES;
    if (platform === "reddit") return REDDIT_COMMUNITIES;
    return []; // Empty for "all" platform
  };

  // Handle platform change - reset community to first option
  const handlePlatformChange = (label) => {
    const selected = PLATFORM_OPTIONS.find((opt) => opt.label === label);
    if (selected) {
      setPlatform(selected.value);
      // Reset community to first option of new platform (or empty for "all")
      if (selected.value === "chan") {
        setCommunity(CHAN_COMMUNITIES[0].value);
      } else if (selected.value === "reddit") {
        setCommunity(REDDIT_COMMUNITIES[0].value);
      } else {
        setCommunity(""); // No community for "all"
      }
    }
  };

  // Handle community change
  const handleCommunityChange = (label) => {
    const options = getCommunityOptions();
    const selected = options.find((opt) => opt.label === label);
    if (selected) {
      setCommunity(selected.value);
    }
  };

  // Handle window change
  const handleWindowChange = (label) => {
    const selected = WINDOW_OPTIONS.find((opt) => opt.label === label);
    if (selected) {
      setWindowSize(selected.value);
    }
  };

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

  const platformFilterOptions = [
    { value: "all", label: "All Platforms" },
    { value: "4chan", label: "4chan" },
    { value: "reddit", label: "Reddit" },
  ];

  // Get current labels for filters
  const currentPlatformLabel =
    PLATFORM_OPTIONS.find((opt) => opt.value === platform)?.label || "4chan";
  const currentCommunityLabel =
    getCommunityOptions().find((opt) => opt.value === community)?.label ||
    community;
  const currentWindowLabel =
    WINDOW_OPTIONS.find((opt) => opt.value === windowSize)?.label || "7 days";

  return (
    <div className="container mx-auto px-10 py-5">
      <div className="grid grid-cols-4 md:grid-cols-4 gap-4">
        <div className="col-span-4">
          {isLoading ? (
            <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white px-5 pt-5 sm:px-6 sm:pt-6 flex items-center justify-center min-h-[300px]">
              <SyncLoader loading={true} color="#465fff" size={26} />
            </div>
          ) : (
            <BarChart
              title="Average Toxicity Per Boards/Subreddit (4chan & Reddit)"
              data={chartData}
              filterLabel={platformFilterOptions.map((opt) => opt.label)}
              defaultFilter={
                platformFilterOptions.find(
                  (opt) => opt.value === selectedPlatform
                )?.label || "All Platforms"
              }
              onFilterChange={({ category }) => {
                const selected = platformFilterOptions.find(
                  (opt) => opt.label === category
                );
                if (selected) {
                  setSelectedPlatform(selected.value);
                }
              }}
            />
          )}
        </div>

        {/* Event Related Timeline Chart */}
        <div className="col-span-3 mt-4">
          {eventLoading ? (
            <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white px-5 pt-5 flex items-center justify-center min-h-[400px]">
              <PropagateLoader loading={true} color="#465fff" />
            </div>
          ) : (
            <LineChart
              title={`Cloudflare Outage Discussion Trends (${eventDate})`}
              data={eventRelatedData}
              showFilters={true}
              filters={[
                {
                  label: "Platform",
                  options: PLATFORM_OPTIONS,
                  selected: currentPlatformLabel,
                  onChange: handlePlatformChange,
                },
                // Only show community filter when a specific platform is selected
                ...(platform !== "all"
                  ? [
                      {
                        label: "Community",
                        options: getCommunityOptions(),
                        selected: currentCommunityLabel,
                        onChange: handleCommunityChange,
                      },
                    ]
                  : []),
                {
                  label: "Window",
                  options: WINDOW_OPTIONS,
                  selected: currentWindowLabel,
                  onChange: handleWindowChange,
                },
              ]}
            />
          )}
        </div>
      </div>
    </div>
  );
}
