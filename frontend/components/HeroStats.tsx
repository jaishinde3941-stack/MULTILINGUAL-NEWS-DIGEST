"use client";

import React, { useMemo } from "react";

interface HeroStatsProps {
  articleCount: number;
}

export const HeroStats: React.FC<HeroStatsProps> = ({ articleCount }) => {
  const formattedDate = useMemo(() => {
    try {
      const now = new Date();
      return now.toLocaleDateString("en-US", {
        weekday: "long",
        month: "long",
        day: "2-digit",
        year: "numeric",
      }).toUpperCase();
    } catch {
      return "SUNDAY, NOVEMBER 01, 2026";
    }
  }, []);

  return (
    <section className="pt-8 sm:pt-10 pb-6 mb-7 border-b border-[var(--border)]">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          {/* Small uppercase date with subtle red accent */}
          <div className="text-[12px] font-medium tracking-widest uppercase text-[var(--accent)] mb-2.5">
            {formattedDate}
          </div>

          {/* Main Editorial Heading in Newsreader */}
          <h1 className="font-editorial text-3xl sm:text-4xl md:text-[44px] lg:text-[48px] font-semibold text-[var(--text-primary)] leading-[1.15] tracking-tight mb-2">
            Your Daily News Briefing
          </h1>

          {/* Clean Subtitle */}
          <p className="text-[15px] sm:text-[16px] text-[var(--text-secondary)] font-normal">
            Global stories. Clear English. One place.
          </p>
        </div>

        {/* Real Article Counter aligned to the right */}
        <div className="text-[13px] sm:text-[14px] text-[var(--text-muted)] font-medium shrink-0 pb-1">
          <span className="text-[var(--text-primary)] font-semibold">{articleCount}</span> Stories
        </div>
      </div>
    </section>
  );
};
