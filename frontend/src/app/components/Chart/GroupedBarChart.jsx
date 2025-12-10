"use client";
import dynamic from "next/dynamic";
import Filter from "../Filter/Filter";

const ReactApexChart = dynamic(() => import("react-apexcharts"), {
  ssr: false,
});

export default function GroupedBarChart({
  title,
  data,
  // Filter props
  filterLabel = [],
  showDropdown = false,
  showDateFilter = false,
  defaultFilter = null,
  startDate = "",
  endDate = "",
  minDate = "",
  maxDate = "",
  onFilterChange = () => {},
}) {
  // Transform data for grouped bar chart
  // Expected data format from API: { data: [{ post_type, total_threads, avg_replies, avg_images, total_replies, norm_* }] }
  const categories = data?.data?.map((item) => item.post_type) || [];
  
  const series = [
    {
      name: "Total Threads",
      data: data?.data?.map((item) => item.norm_total_threads || 0) || [],
    },
    {
      name: "Avg Replies",
      data: data?.data?.map((item) => item.norm_avg_replies || 0) || [],
    },
    {
      name: "Total Replies",
      data: data?.data?.map((item) => item.norm_total_replies || 0) || [],
    },
    {
      name: "Avg Images",
      data: data?.data?.map((item) => item.norm_avg_images || 0) || [],
    },
  ];

  const options = {
    chart: {
      type: "bar",
      height: 350,
      fontFamily: "Outfit, sans-serif",
      toolbar: {
        show: false,
      },
    },
    colors: ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6"],
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: "55%",
        endingShape: "rounded",
        borderRadius: 5,
      },
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      show: true,
      width: 2,
      colors: ["transparent"],
    },
    xaxis: {
      categories: categories,
      labels: {
        style: {
          fontSize: "12px",
          colors: "#6B7280",
        },
      },
    },
    yaxis: {
      title: {
        text: "Normalized Score (0-1)",
        style: {
          fontSize: "12px",
          color: "#6B7280",
        },
      },
      min: 0,
      max: 1,
      labels: {
        style: {
          fontSize: "12px",
          colors: "#6B7280",
        },
        formatter: function (val) {
          return val.toFixed(2);
        },
      },
    },
    fill: {
      opacity: 1,
    },
    tooltip: {
      theme: "dark",
      y: {
        formatter: function (val, { seriesIndex, dataPointIndex, w }) {
          const dataItem = data?.data?.[dataPointIndex];
          if (!dataItem) return val;
          
          // Return actual values from the data
          if (seriesIndex === 0) {
            return `${dataItem.total_threads.toLocaleString()} threads`;
          } else if (seriesIndex === 1) {
            return `${dataItem.avg_replies.toFixed(2)} replies`;
          } else if (seriesIndex === 2) {
            return `${dataItem.total_replies.toLocaleString()} replies`;
          } else if (seriesIndex === 3) {
            return `${dataItem.avg_images.toFixed(2)} images`;
          }
          return val;
        },
      },
    },
    legend: {
      position: "top",
      horizontalAlign: "left",
      fontSize: "12px",
      markers: {
        radius: 2,
      },
    },
    grid: {
      borderColor: "#F3F4F6",
      yaxis: {
        lines: {
          show: true,
        },
      },
    },
  };

  // Handle dropdown change
  const handleOptionChange = (option) => {
    onFilterChange({ category: option });
  };

  // Handle date apply
  const handleDateChange = ({ startDate: newStart, endDate: newEnd }) => {
    onFilterChange({ startDate: newStart, endDate: newEnd });
  };

  return (
    <div className="overflow-hidden rounded-2xl border bg-white px-5 pt-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          {title || "Engagement by Post Type"}
        </h3>

        {/* Filter Component */}
        {(showDropdown || showDateFilter) && (
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
        )}
      </div>
      <ReactApexChart
        options={options}
        series={series}
        type="bar"
        height={350}
      />
    </div>
  );
}
