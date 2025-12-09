"use client";
import React from "react";

export default function StatsCards({ items }) {
  if (!items) return null;

  // Allow both array and object (dictionary)
  const list = Array.isArray(items) ? items : Object.values(items);

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 mb-4">
      {list.map((item, idx) => {
        const colorClass =
          item.color === "orange"
            ? "bg-orange-100 text-orange-600"
            : item.color === "purple"
            ? "bg-purple-100 text-purple-600"
            : item.color === "blue"
            ? "bg-sky-100 text-sky-600"
            : "bg-emerald-100 text-emerald-600"; // default green

        const trendColor =
          typeof item.trend === "number" && item.trend < 0
            ? "text-red-500"
            : "text-emerald-500";

        return (
          <div
            key={item.key || idx}
            className="overflow-hidden rounded-2xl border border-gray-200 bg-white px-5 py-4  flex flex-col justify-between"
          >
            {/* Top row: icon + value */}
            <div className="flex items-center gap-4">
              <div
                className={`flex h-12 w-12 items-center justify-center rounded-full ${colorClass}`}
              >
                <span className="text-xl">{item.icon || "•"}</span>
              </div>

              <div>
                <div className="text-xs font-medium text-gray-500">
                  {item.label}
                </div>
                <div className="text-2xl font-semibold text-gray-900 ">
                  {item.value}
                </div>
              </div>
            </div>

            {/* Bottom row: helper text + optional trend */}
            {(item.helper || typeof item.trend !== "undefined") && (
              <div className="mt-3 flex items-center justify-between text-xs">
                {item.helper && (
                  <span className="text-gray-400">{item.helper}</span>
                )}
                {typeof item.trend !== "undefined" && (
                  <span className={trendColor}>
                    {item.trend > 0 ? "+" : ""}
                    {item.trend}%
                    {item.trend > 0 ? " ↑" : item.trend < 0 ? " ↓" : ""}
                  </span>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
