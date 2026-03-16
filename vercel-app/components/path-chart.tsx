"use client";

import type { EChartsOption } from "echarts";

import { EChartPanel } from "@/components/echart-panel";
import type { PathsPayload } from "@/lib/types";

const palette = ["#4ed7ff", "#f6b94a", "#59f2a3", "#ff8bca", "#ff6d78", "#9f8cff"];

export function PathChart({ payload }: { payload: PathsPayload }) {
  const option: EChartsOption = {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis",
      valueFormatter: (value) => `${Number(value).toFixed(2)}%`,
    },
    legend: {
      top: 8,
      textStyle: { color: "#95a7c7" },
    },
    grid: { left: 48, right: 24, top: 48, bottom: 34 },
    xAxis: {
      type: "category",
      data: payload.days,
      axisLine: { lineStyle: { color: "rgba(255,255,255,0.14)" } },
      axisLabel: { color: "#95a7c7" },
    },
    yAxis: {
      type: "value",
      axisLine: { show: false },
      splitLine: { lineStyle: { color: "rgba(255,255,255,0.08)" } },
      axisLabel: { color: "#95a7c7", formatter: "{value}%" },
    },
    series: payload.series.map((series, index) => ({
      type: "line",
      name: series.displayLabel,
      data: series.values,
      smooth: true,
      showSymbol: false,
      lineStyle: {
        width: 3,
        color: palette[index % palette.length],
      },
    })),
  };

  return <EChartPanel option={option} />;
}
