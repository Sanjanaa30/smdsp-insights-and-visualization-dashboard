"use client";
import dynamic from "next/dynamic";
import Filter from "../Filter/Filter";

// Dynamically import the ReactApexChart component
const ReactApexChart = dynamic(() => import("react-apexcharts"), {
  ssr: false,
});

export default function LineChart({
  title,
  filterLabel = [], // array of categories
  data,
  datesEnabled = false,
  onApplyFilters = () => {},
  defaultFilter = null,
  // New: array of filter configs
  showFilters = false,
  filters = [], // [{ label, options, selected, onChange }]
}) {
  // Detect data format and transform accordingly
  let categories = [];
  let series = [];

  // Check if data is timeline format (single series with date/count)
  if (data?.timeline) {
    // Timeline format: { platform, community, timeline: [{ date, count }] }
    categories = data.timeline.map((item) => item.date);
    series = [
      {
        name: data.community || "Count",
        data: data.timeline.map((item) => item.count),
      },
    ];
  } else if (data?.data) {
    // Multi-series format: { data: [{ date, subreddit_counts: { ... } }] }
    categories = data.data.map((item) => item.date);

    // Get all unique subreddit names
    const subredditNames =
      data.data.length > 0 ? Object.keys(data.data[0].subreddit_counts) : [];

    // Create series data for each subreddit
    series = subredditNames.map((subredditName) => ({
      name: subredditName.charAt(0).toUpperCase() + subredditName.substring(1),
      data: data.data.map((item) => item.subreddit_counts[subredditName] || 0),
    }));
  }

  const options = {
    // legend: {
    //   show: true, // Show legend to identify subreddits
    //   position: "top",
    //   horizontalAlign: "left",
    // },
    colors: ["#465FFF", "#9CB9FF", "#FF6B6B"], // Define line colors
    chart: {
      fontFamily: "Outfit, sans-serif",
      height: 310,
      type: "line", // Set the chart type to 'line'
      toolbar: {
        show: true, // Hide chart toolbar
        export: {
          csv: {
            filename: "Daily Posts By Subreddits",
          },
          svg: {
            filename: "Daily Posts By Subreddits",
          },
          png: {
            filename: "Daily Posts By Subreddits",
          },
        },
      },
    },
    stroke: {
      curve: "straight", // Define the line style (straight, smooth, or step)
      width: 2, // Line width for each dataset
    },

    fill: {
      type: "gradient",
      gradient: {
        opacityFrom: 0.55,
        opacityTo: 0,
      },
    },
    markers: {
      size: 0, // Size of the marker points
      strokeColors: "#fff", // Marker border color
      strokeWidth: 2,
      hover: {
        size: 6, // Marker size on hover
      },
    },
    grid: {
      xaxis: {
        lines: {
          show: false, // Hide grid lines on x-axis
        },
      },
      yaxis: {
        lines: {
          show: true, // Show grid lines on y-axis
        },
      },
    },
    dataLabels: {
      enabled: false, // Disable data labels
    },
    tooltip: {
      theme: "dark",
    },
    xaxis: {
      type: "category", // Category-based x-axis
      categories: categories,
      axisBorder: {
        show: false, // Hide x-axis border
      },
      axisTicks: {
        show: false, // Hide x-axis ticks
      },
      tooltip: {
        theme: true,
        enabled: true,
      },
    },
    yaxis: {
      labels: {
        style: {
          fontSize: "12px", // Adjust font size for y-axis labels
          colors: ["#6B7280"], // Color of the labels
        },
      },
      title: {
        text: "", // Remove y-axis title
        style: {
          fontSize: "0px",
        },
      },
    },
  };
  return (
    <div className="overflow-hidden rounded-2xl border bg-white px-5 pt-5 relative">
      <div className="flex items-center justify-between mb-4">
        {/* LEFT: Title */}
        <h3 className="text-lg font-semibold text-gray-800">
          {title || "Daily Posts"}
        </h3>

        {/* RIGHT: Filters */}
        {showFilters && filters.length > 0 && (
          <div className="flex items-center gap-2">
            {filters.map((filter, index) => (
              <Filter
                key={index}
                showDropdown={true}
                showDateFilter={false}
                dropdownOptions={filter.options}
                selectedOption={filter.selected}
                dropdownLabel={filter.label}
                onOptionChange={filter.onChange}
              />
            ))}
          </div>
        )}
      </div>
      <ReactApexChart
        options={options}
        series={series}
        type="area"
        height={310}
      />
    </div>
  );
}
