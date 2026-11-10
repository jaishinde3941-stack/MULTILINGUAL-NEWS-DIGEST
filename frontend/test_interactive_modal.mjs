import { createJiti } from "jiti";
import React, { act } from "react";
import ReactDOMServer from "react-dom/server";
import assert from "node:assert";

const jiti = createJiti(import.meta.url, {
  alias: {
    "@": new URL("./", import.meta.url).pathname.replace(/^\/([A-Z]:)/, "$1"),
  },
  jsx: {
    runtime: "automatic"
  }
});

const { ArticleReaderModal } = await jiti.import("./components/ArticleReaderModal.tsx");

console.log("=== Premium Editorial Modal Test Suite ===");

// 1. Fetch real articles from backend API to test real data from the actual database
const response = await fetch("http://127.0.0.1:8000/api/articles?limit=30");
const data = await response.json();
const realArticles = data.items;

console.log(`Retrieved ${realArticles.length} live articles from backend API.`);

// Group articles by original language
const byLang = new Map();
for (const art of realArticles) {
  if (!byLang.has(art.original_language)) {
    byLang.set(art.original_language, []);
  }
  byLang.get(art.original_language).push(art);
}

console.log(`Found live languages: ${Array.from(byLang.keys()).join(", ")}`);

// Verify modal rendering for each language from the real database
for (const [lang, articles] of byLang.entries()) {
  const article = articles[0];
  console.log(`\nTesting Real Article in ${lang}: ID #${article.id} (${article.source_name})`);

  let closed = false;
  const html = ReactDOMServer.renderToStaticMarkup(
    React.createElement(ArticleReaderModal, {
      article,
      onClose: () => { closed = true; },
    })
  );

  // 1. Check Header
  assert(html.includes(article.source_name), `Header must contain source name '${article.source_name}'`);
  assert(html.includes(`${article.original_language}`), `Header must contain original language '${lang}'`);
  assert(html.includes("English"), `Header must contain target language English`);
  assert(html.includes("Listen"), `Header must have Listen voice reader control`);
  assert(html.includes("Copy"), `Header must have Copy button`);
  assert(html.includes("Source"), `Header must have original source button`);
  assert(html.includes("btn-close-reader-modal"), `Header must have Close button with id btn-close-reader-modal`);

  // 2. Check Prominent English Headline (React escapes apostrophes to &#x27;)
  const escapedTitle = article.english_title.replace(/'/g, "&#x27;").replace(/"/g, "&quot;");
  assert(html.includes(escapedTitle) || html.includes(article.english_title), `Modal must feature the prominent English headline`);
  assert(html.includes("font-bold"), `Headline must use bold typography`);

  // 3. Check Subtle Metadata above headline
  assert(html.includes(article.field || "General News"), `Editorial field must be displayed above headline`);
  assert(html.includes(article.region), `Geographic region must be displayed above headline`);

  // 4. Check Original Language Headline is hidden by default and expandable button is present
  const expectedExpandBtn = `View Original Headline (${article.original_language})`;
  assert(html.includes(expectedExpandBtn), `Must have dynamic expand button: '${expectedExpandBtn}'`);
  assert(!html.includes(`&ldquo;${article.original_title}&rdquo;`), `Original title must NOT be expanded by default`);

  // 5. Check Central English Executive Summary
  assert(html.toUpperCase().includes("EXECUTIVE SUMMARY"), `Must have clean 'Executive Summary' section header`);
  const summarySlice = article.english_summary.split("\n")[0].trim().slice(0, 30).replace(/'/g, "&#x27;");
  assert(html.includes(summarySlice), `Must render English executive summary`);
  if (article.summary_word_count && article.summary_word_count > 0) {
    assert(html.includes(`${article.summary_word_count} words`), `Must display word count as subtle metadata`);
  }

  // 6. Check Compact Editorial Source Footer
  assert(html.includes("Original source:"), `Footer must indicate 'Original source:'`);
  assert(html.includes("Read Full Story") || html.includes("Read Original Article"), `Footer must include 'Read Full Story' link`);
  assert(html.includes(article.source_url), `Source link must point to actual publisher URL`);

  // 7. Check Contextual Tags
  assert(html.includes("Tags:"), `Must render Contextual Tags`);
  // Must NOT include rainbow colors (violet, teal, blue, emerald)
  assert(!html.includes("text-violet-"), `Must not use violet rainbow color for tags`);
  assert(!html.includes("text-emerald-"), `Must not use emerald rainbow color for tags`);
  assert(!html.includes("text-teal-"), `Must not use teal rainbow color for tags`);
  // Must use subtle red accent for lead tag
  assert(html.includes("bg-[var(--accent-soft)]") || html.includes("bg-[var(--accent-subtle)]"), `Lead tag must have subtle editorial red accent`);
  // Must use neutral styling for remaining tags
  assert(html.includes("bg-[var(--surface-secondary)]") || html.includes("bg-[var(--bg-subtle)]"), `Tags must use neutral styling`);

  console.log(`✓ Real article #${article.id} (${lang}) passed all editorial requirements!`);
}

// 8. Test Edge Case: Article with no keywords or generic keywords
console.log("\nTesting Tag Fallback and Synthesis for sparse article...");
const sparseArticle = {
  id: 9999,
  source_url: "https://example.com/test",
  source_name: "The Diplomatic Post",
  original_language: "Marathi",
  original_title: "निवडणूक आणि नेतृत्व चर्चा",
  original_content: "Content...",
  english_title: "Election Leadership and Diplomacy Reshuffle Announced",
  english_summary: "The cabinet announced key election and diplomacy leadership updates today.",
  english_content: "The cabinet announced key election and diplomacy leadership updates today.",
  region: "National",
  field: "Politics",
  keywords: ["States & Regional", "News", "General"], // All generic keywords!
  trending: false,
  trending_score: 0.5,
  published_at: "2026-11-01T10:00:00Z",
  created_at: "2026-11-01T10:00:00Z",
};

const htmlSparse = ReactDOMServer.renderToStaticMarkup(
  React.createElement(ArticleReaderModal, {
    article: sparseArticle,
    onClose: () => {},
  })
);

// Generic tags must be filtered out
assert(!htmlSparse.includes("STATES &amp; REGIONAL") && !htmlSparse.includes("STATES & REGIONAL"));
assert(!htmlSparse.includes("NEWS"));
// High-value inferred tags must be synthesized (2-4 tags)
assert(htmlSparse.includes("POLITICS"), "Should include POLITICS field tag");
assert(htmlSparse.includes("ELECTION"), "Should include synthesized ELECTION tag");
assert(htmlSparse.includes("DIPLOMACY"), "Should include synthesized DIPLOMACY tag");

console.log("✓ Tag synthesis and generic filtering passed!");

console.log("\n==========================================");
console.log("ALL REAL ARTICLE AND UNIT TESTS PASSED!");
console.log("==========================================");
