"use client";

import type { EChartsOption } from "echarts";

import { EChartPanel } from "@/components/echart-panel";
import type { HeatmapPayload } from "@/lib/types";

export function HeatmapChart({ payload }: { payload: HeatmapPayload }) {
  const data = payload.assets.flatMap((asset, assetIndex) =>
    payload.horizons.map((horizon, horizonIndex) => [
      horizonIndex,
      assetIndex,
      payload.values[assetIndex]?.[horizonIndex] ?? 0,
      asset,
      horizon,
    ]),
  );

  const option: EChartsOption = {
    backgroundColor: "transparent",
    tooltip: {
      formatter: (params: any) => {
        const [, , value, asset, horizon] = params.data as [number, number, number, string, string];
        return `${asset}<br/>${horizon}: ${value.toFixed(2)}%`;
      },
    },
    grid: { left: 110, right: 24, top: 12, bottom: 72 },
    xAxis: {
      type: "category",
      data: payload.horizons,
      axisLine: { lineStyle: { color: "rgba(255,255,255,0.14)" } },
      axisLabel: { color: "#95a7c7" },
    },
    yAxis: {
      type: "category",
      data: payload.assets,
      axisLine: { lineStyle: { color: "rgba(255,255,255,0.14)" } },
      axisLabel: { color: "#f4f8ff" },
    },
    visualMap: {
      min: -8,
      max: 8,
      calculable: true,
      orient: "horizontal",
      left: "center",
      bottom: 8,
      inRange: {
        color: ["#ff6d78", "#1b1f2e", "#4ed7ff"],
      },
      textStyle: { color: "#95a7c7" },
    },
    series: [
      {
        type: "heatmap",
        data,
        label: {
          show: true,
          color: "#f4f8ff",
          formatter: (params: any) => (params.data as [number, number, number])[2].toFixed(1),
        },
        emphasis: {
          itemStyle: {
            borderColor: "rgba(255,255,255,0.4)",
            borderWidth: 1,
          },
        },
      },
    ],
  };

  return <EChartPanel option={option} />;
}
