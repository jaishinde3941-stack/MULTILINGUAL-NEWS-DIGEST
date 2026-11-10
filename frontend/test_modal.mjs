import { createJiti } from "jiti";
import React from "react";
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

console.log("Successfully loaded ArticleReaderModal component!");

const sampleMarathiArticle = {
  id: 271,
  source_url: "https://marathi.abplive.com/news/maharashtra/fake-police-case",
  source_name: "ABP Live",
  original_language: "Marathi",
  original_title: "भिवंडीः फेक पुलिस और कॉपीराइट केस",
  original_content: "संपूर्ण बातमीचा तपशील...",
  english_title: "Bhiwandi: Fake Police and Extortion Ring Busted in Raid",
  english_summary: "Police in Bhiwandi have dismantled an extortion gang posing as police and copyright enforcement officials. The accused were extorting local merchants under threat of fabricated copyright violations. Authorities seized forged credentials and fake enforcement insignia during the overnight operation.",
  english_content: "Police in Bhiwandi have dismantled an extortion gang...",
  region: "Maharashtra",
  subregion: "Western India",
  field: "Crime & Law",
  keywords: ["Extortion", "Police", "Bhiwandi", "States & Regional"],
  trending: false,
  trending_score: 0.8,
  processing_status: "completed",
  summary_word_count: 36,
  published_at: "2026-11-01T12:00:00Z",
  created_at: "2026-11-01T12:05:00Z",
};

// 1. Render Marathi Article
const htmlMarathi = ReactDOMServer.renderToStaticMarkup(
  React.createElement(ArticleReaderModal, {
    article: sampleMarathiArticle,
    onClose: () => {},
  })
);

// Verify Header elements
assert(htmlMarathi.includes("ABP Live"), "Header should display publication name");
assert(htmlMarathi.includes("Marathi"), "Header should display original language");
assert(htmlMarathi.includes("English"), "Header should display target language English");
assert(htmlMarathi.includes("Listen"), "Header should display Listen button");
assert(htmlMarathi.includes("Copy"), "Header should display Copy button");
assert(htmlMarathi.includes("Source"), "Header should display Source link");
assert(htmlMarathi.includes("btn-close-reader-modal"), "Header should display close button");

// Verify English Headline is prominent
assert(htmlMarathi.includes("Bhiwandi: Fake Police and Extortion Ring Busted in Raid"), "English headline must be rendered");
assert(htmlMarathi.includes("Crime &amp; Law") || htmlMarathi.includes("Crime & Law"), "Editorial field must be rendered above headline");
assert(htmlMarathi.includes("Maharashtra"), "Geographical region must be rendered above headline");

// Verify Original Language Headline is hidden by default and expandable button is present
assert(htmlMarathi.includes("View Original Headline (Marathi)"), "Expandable control for Marathi headline must be present");
assert(!htmlMarathi.includes("भिवंडीः फेक पुलिस और कॉपीराइट केस"), "Original Marathi headline must NOT be displayed by default");

// Verify English Executive Summary
assert(htmlMarathi.toUpperCase().includes("EXECUTIVE SUMMARY"), "Executive Summary section label must be present");
assert(htmlMarathi.includes("36 words"), "Word count must be displayed as subtle metadata");
assert(htmlMarathi.includes("Police in Bhiwandi have dismantled an extortion gang"), "Summary content must be present in English");

// Verify Compact Editorial Footer
assert(htmlMarathi.includes("Original source:"), "Footer must have 'Original source:' label");
assert(htmlMarathi.includes("Read Full Story") || htmlMarathi.includes("Read Original Article"), "Footer must have 'Read Full Story' or 'Read Original Article' link");
assert(htmlMarathi.includes("https://marathi.abplive.com/news/maharashtra/fake-police-case"), "External link must open original URL");

// Verify Contextual Tags (2-4 tags, English only, generic terms filtered)
assert(!htmlMarathi.includes("STATES &amp; REGIONAL") && !htmlMarathi.includes("STATES & REGIONAL"), "Generic term 'States & Regional' must be filtered out");
assert(htmlMarathi.includes("EXTORTION"), "Expected tag EXTORTION");
assert(htmlMarathi.includes("POLICE"), "Expected tag POLICE");

console.log("All Marathi article assertions PASSED!");

// 2. Test other languages dynamically: Telugu, Gujarati, Hindi, Tamil, Malayalam
const testLanguages = [
  { lang: "Telugu", title: "తెలుగు వార్తలు శీర్షిక", englishTitle: "Andhra Pradesh Announces Clean Tech Subsidies" },
  { lang: "Gujarati", title: "ગુજરાતી સમાચાર હેડલાઇન", englishTitle: "Gujarat Expands Solar Park Capacity" },
  { lang: "Hindi", title: "इसरो ने गगनयान के लिए इंजन का सफल परीक्षण किया", englishTitle: "ISRO Successfully Tests Cryogenic Engine for Gaganyaan" },
  { lang: "Tamil", title: "சென்னை மெட்ரோ திட்டம் புதிய அறிவிப்பு", englishTitle: "Chennai Metro Phase II Expansion Underway" },
  { lang: "Malayalam", title: "കേരളത്തിൽ പുതിയ ഐടി പദ്ധതി", englishTitle: "Kerala Launches Next-Gen AI Startup Hub" },
];

for (const item of testLanguages) {
  const art = {
    ...sampleMarathiArticle,
    id: sampleMarathiArticle.id + 1,
    original_language: item.lang,
    original_title: item.title,
    english_title: item.englishTitle,
  };

  const html = ReactDOMServer.renderToStaticMarkup(
    React.createElement(ArticleReaderModal, {
      article: art,
      onClose: () => {},
    })
  );

  assert(html.includes(`View Original Headline (${item.lang})`), `Must dynamically show View Original Headline (${item.lang})`);
  assert(!html.includes(item.title), `Original headline for ${item.lang} must be hidden by default`);
  assert(html.includes(item.englishTitle), `English headline for ${item.lang} must be shown`);
  console.log(`Language test for ${item.lang} PASSED!`);
}

// 3. Test null article unmounting
const htmlNull = ReactDOMServer.renderToStaticMarkup(
  React.createElement(ArticleReaderModal, {
    article: null,
    onClose: () => {},
  })
);
assert.strictEqual(htmlNull, "", "Modal must render nothing when article is null");
console.log("Null unmount test PASSED!");

console.log("ALL TESTS COMPLETED SUCCESSFULLY!");

