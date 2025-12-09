"use client";
import dynamic from "next/dynamic";
import { FiChevronDown } from "react-icons/fi";
import { useState } from "react";

const ReactApexChart = dynamic(() => import("react-apexcharts"), {
  ssr: false,
});

export default function BarChart({
  title,
  filterLabel = [], // array of categories
  data,
  datesEnabled = false,
  onApplyFilters = () => {},
  defaultFilter = null, // NEW: controlled filter value from parent
}) {
  // Chart Data
  const categories = data?.map((item) => item.day) || [];
  const counts = data?.map((item) => item.count) || [];

  const options = {
    colors: ["#465fff"],
    chart: {
      fontFamily: "Outfit, sans-serif",
      type: "bar",
      height: 180,
      toolbar: { show: false },
    },
    plotOptions: {
      bar: {
        columnWidth: "39%",
        borderRadius: 5,
        borderRadiusApplication: "end",
      },
    },
    dataLabels: { enabled: false },
    stroke: {
      show: true,
      width: 4,
      colors: ["transparent"],
    },
    xaxis: {
      categories,
      axisBorder: { show: false },
      axisTicks: { show: false },
    },
    yaxis: {
      labels: {
        style: { colors: "#9CA3AF", fontSize: "12px" },
      },
    },
    grid: {
      borderColor: "#F3F4F6",
      yaxis: { lines: { show: true } },
    },
    tooltip: {
      theme: "dark",
      y: { formatter: (val) => `${val} posts` },
    },
  };

  const series = [
    {
      name: title || "Posts",
      data: counts,
    },
  ];

  // Filter States - use defaultFilter from parent if provided
  const [filterOpen, setFilterOpen] = useState(false);
  const selectedFilter = defaultFilter || filterLabel?.[0] || "All";
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  function toggleFilter() {
    setFilterOpen(!filterOpen);
  }

  return (
    <div className="overflow-hidden rounded-2xl border bg-white px-5 pt-5 relative">
      {/* HEADER */}
      <div className="flex items-center justify-between mb-4">
        {/* LEFT: Title */}
        <h3 className="text-lg font-semibold text-gray-800">
          {title || "Daily Posts"}
        </h3>

        {/* RIGHT: Filters + Date Inputs */}
        <div className="flex items-center gap-3">
          {/* DATE INPUTS (SIDE BY SIDE, NOT IN DROPDOWN) */}
          {datesEnabled && (
            <div className="flex items-center gap-2">
              {/* Start Date */}
              <input
                type="date"
                value={startDate}
                min="2025-11-01"
                onChange={(e) => {
                  const newDate = e.target.value;

                  // Optional: guard in JS as well
                  if (newDate < "2025-11-01") return;

                  setStartDate(newDate);
                  onApplyFilters({
                    category: selectedFilter,
                    startDate: newDate,
                    endDate,
                  });
                }}
                className="border px-2 py-1 rounded-md text-sm text-black"
              />

              {/* End Date */}
              <input
                type="date"
                value={endDate}
                onChange={(e) => {
                  setEndDate(e.target.value);
                  onApplyFilters({
                    category: selectedFilter,
                    startDate,
                    endDate: e.target.value,
                  });
                }}
                className="border px-2 py-1 rounded-md text-sm text-black"
              />
            </div>
          )}

          {/* FILTER DROPDOWN */}
          <div className="relative">
            <button
              onClick={toggleFilter}
              className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium 
                       text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
            >
              {selectedFilter}
              <FiChevronDown className="text-gray-500" />
            </button>

            {/* DROPDOWN CONTENT */}
            {filterOpen && (
              <div
                className="absolute right-0 mt-2 z-30 bg-white shadow-md border 
                         rounded-xl p-3 w-40"
              >
                {Array.isArray(filterLabel) &&
                  filterLabel.map((option) => (
                    <button
                      key={option}
                      onClick={() => {
                        onApplyFilters({
                          category: option,
                          startDate,
                          endDate,
                        });

                        setFilterOpen(false);
                      }}
                      className="block text-left py-1 text-xs 
                               rounded-md hover:bg-gray-100 text-gray-700"
                    >
                      {option}
                    </button>
                  ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* CHART */}
      <ReactApexChart
        options={options}
        series={series}
        type="bar"
        height={200}
      />
    </div>
  );
}
