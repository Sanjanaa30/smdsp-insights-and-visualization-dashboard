"use client";

import dynamic from "next/dynamic";
const Chart = dynamic(() => import("react-apexcharts"), { ssr: false });

export default function HorizontalBarChart({ title, categories, series }) {
  const options = {
    chart: {
      type: "bar",
      toolbar: { show: false },
      foreColor: "#9CA3AF",
      events: {
        dataPointSelection: (event, chartContext, config) => {
          const clickedIndex = config.dataPointIndex;
          const url = categories[clickedIndex];
          window.open(`https://www.reddit.com/r/${url}`, '_blank');
        },
      },
    },
    plotOptions: {
      bar: {
        horizontal: true,
        barHeight: "60%",
        borderRadius: 0, // ⬅ NO ROUNDED CORNERS
        dataLabels: {
          position: "center", // ⬅ TEXT INSIDE BARS
        },
      },
    },

    states: {
      hover: {
        filter: { type: "none" }, // ⬅ NO COLOR CHANGE ON HOVER
      },
      active: {
        filter: { type: "none" }, // ⬅ NO DARKENING ON CLICK
      },
    },

    dataLabels: {
      enabled: true,
      style: {
        fontSize: "12px",
        colors: ["#4B5563"], // ⬅ DARK GREY TEXT
        fontWeight: 600,
      },
      offsetX: 0,
    },

    colors: ["#D1D5DB"], // ⬅ SAME GREY ALWAYS

    grid: {
      borderColor: "#E5E7EB",
      strokeDashArray: 4,
      padding: { left: 20 },
    },

    xaxis: {
      categories,
      labels: { style: { colors: "#9CA3AF" } },
    },

    yaxis: {
      labels: {
        style: { colors: "#374151", fontWeight: 500 },
        maxWidth: 300,
      },
    },

    tooltip: { enabled: false }, // OPTIONAL: cleaner UI
    legend: { show: false }, // Hides legend since 1 series
  };

  return (
    <div className="overflow-hidden rounded-2xl border bg-white px-5 pt-5 relative">
      <div className="flex items-center justify-between mb-4">
        {/* LEFT: Title */}
        <h3 className="text-lg font-semibold text-gray-800">
          {title || "Daily Posts"}
        </h3>
      </div>
      <Chart options={options} series={series} type="bar" height={550} />
    </div>
  );
}
