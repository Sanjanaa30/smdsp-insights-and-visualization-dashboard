"use client";
import dynamic from "next/dynamic";
import Filter from "../Filter/Filter";

const ReactApexChart = dynamic(() => import("react-apexcharts"), {
  ssr: false,
});

export default function BarChart({
  title,
  filterLabel = [], // array of categories
  data,
  showDateFilter = false,
  showDropdown = true,
  onFilterChange = () => {},
  defaultFilter = null,
  startDate = "",
  endDate = "",
  minDate = "",
  maxDate = "",
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

  // Handle dropdown change
  const handleOptionChange = (option) => {
    onFilterChange({ category: option });
  };

  // Handle date apply
  const handleDateChange = ({ startDate: newStart, endDate: newEnd }) => {
    onFilterChange({ startDate: newStart, endDate: newEnd });
  };

  return (
    <div className="overflow-hidden rounded-2xl border bg-white px-5 pt-5 relative">
      {/* HEADER */}
      <div className="flex items-center justify-between mb-4">
        {/* LEFT: Title */}
        <h3 className="text-lg font-semibold text-gray-800">
          {title || "Daily Posts"}
        </h3>

        {/* RIGHT: Filter Component */}
        <Filter
          showDropdown={showDropdown}
          dropdownOptions={filterLabel}
          selectedOption={defaultFilter}
          onOptionChange={handleOptionChange}
          showDateFilter={showDateFilter}
          startDate={startDate}
          endDate={endDate}
          minDate={minDate}
          maxDate={maxDate}
          onDateChange={handleDateChange}
        />
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
