"use client";

import dynamic from "next/dynamic";
import type { EChartsOption } from "echarts";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

export function EChartPanel({
  option,
  compact = false,
}: {
  option: EChartsOption;
  compact?: boolean;
}) {
  return (
    <div className={`panel panel-card ${compact ? "chart-frame-compact" : "chart-frame"}`}>
      <ReactECharts option={option} style={{ height: compact ? 320 : 380, width: "100%" }} />
    </div>
  );
}
