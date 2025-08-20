# MyFoodBudget – Mobile‑First UI Design Spec (Light/Dark, Calm Trust)

This document contains everything needed to recreate the mobile UI in your IDE: color tokens, CSS utilities, component guidelines, and a reference React implementation.

---

## 1) Design Principles (concise)

* Less, but clearer: neutral surfaces, restrained accent usage.
* Trust first: Calm blue for actions, green for positive finance semantics.
* Explicit status semantics: green=success, amber=warning, red=danger; never mix.
* Mobile ergonomics: large tap targets (≥44px), clear hierarchy, sticky nav/header.
* Accessibility: WCAG 2.1 AA for text; visible focus outlines; no color‑only cues.

---

## 2) Color System (Tokens)

### 2.1 Light Theme Tokens

| Token           | Hex       | Usage                                        |
| --------------- | --------- | -------------------------------------------- |
| `--primary-700` | `#1A56C7` | Hover/high emphasis actions                  |
| `--primary-600` | `#1E63E9` | Primary actions, active states, links        |
| `--primary-100` | `#EAF2FF` | Blue wash backgrounds, chart fills           |
| `--success-600` | `#1FA36A` | Positive/under‑budget fills, success buttons |
| `--success-100` | `#E8F7F0` | Success wash surfaces                        |
| `--warning-600` | `#B98500` | Approaching limit, non‑destructive cautions  |
| `--warning-100` | `#FFF6DF` | Warning wash surfaces                        |
| `--danger-600`  | `#D64545` | Destructive actions, overspend               |
| `--danger-100`  | `#FFE9E9` | Danger wash surfaces                         |
| `--bg`          | `#F6F7F9` | App background                               |
| `--surface`     | `#FFFFFF` | Cards, sheets                                |
| `--muted`       | `#F1F3F5` | Tracks, muted chips                          |
| `--border`      | `#E5E7EB` | Dividers, borders                            |
| `--text-900`    | `#0F172A` | Primary text                                 |
| `--text-700`    | `#334155` | Secondary headings                           |
| `--text-500`    | `#64748B` | Secondary text                               |

### 2.2 Dark Theme Tokens

| Token           | Hex       | Usage                                 |
| --------------- | --------- | ------------------------------------- |
| `--primary-700` | `#76A7FF` | Hover/high emphasis actions           |
| `--primary-600` | `#8CB6FF` | Primary actions, active states, links |
| `--primary-100` | `#0E213F` | Blue wash backgrounds, chart fills    |
| `--success-600` | `#7BDFAD` | Positive/under‑budget fills           |
| `--success-100` | `#0E2A1F` | Success wash surfaces                 |
| `--warning-600` | `#F6D385` | Approaching limit                     |
| `--warning-100` | `#2B230A` | Warning wash surfaces                 |
| `--danger-600`  | `#FFA3A3` | Destructive/overspend                 |
| `--danger-100`  | `#2E0F12` | Danger wash surfaces                  |
| `--bg`          | `#0C0F14` | App background                        |
| `--surface`     | `#151922` | Cards, sheets                         |
| `--muted`       | `#1C2230` | Tracks, muted chips                   |
| `--border`      | `#2A3446` | Dividers, borders                     |
| `--text-900`    | `#F8FAFC` | Primary text                          |
| `--text-700`    | `#E2E8F0` | Secondary headings                    |
| `--text-500`    | `#94A3B8` | Secondary text                        |

### 2.3 Semantic Mapping

* Actions/selection: **primary‑600**.
* Success/progress OK: **success‑600** (fills) on **muted** tracks.
* Warning/near limit: **warning‑600** border on **warning‑100** surface.
* Danger/overspend: **danger‑600** border on **danger‑100** surface.
* Surfaces/text: **surface/border/text‑900/700/500**.

---

## 3) CSS Variables and Utilities (drop‑in)

Place this in a global stylesheet, e.g., `src/styles/tokens.css`.

```css
:root {
  --primary-700: #1A56C7;
  --primary-600: #1E63E9;
  --primary-100: #EAF2FF;

  --success-600: #1FA36A;
  --success-100: #E8F7F0;

  --warning-600: #B98500;
  --warning-100: #FFF6DF;

  --danger-600: #D64545;
  --danger-100: #FFE9E9;

  --bg: #F6F7F9;
  --surface: #FFFFFF;
  --muted: #F1F3F5;
  --border: #E5E7EB;

  --text-900: #0F172A;
  --text-700: #334155;
  --text-500: #64748B;
}

[data-theme="dark"] {
  --primary-700: #76A7FF;
  --primary-600: #8CB6FF;
  --primary-100: #0E213F;

  --success-600: #7BDFAD;
  --success-100: #0E2A1F;

  --warning-600: #F6D385;
  --warning-100: #2B230A;

  --danger-600: #FFA3A3;
  --danger-100: #2E0F12;

  --bg: #0C0F14;
  --surface: #151922;
  --muted: #1C2230;
  --border: #2A3446;

  --text-900: #F8FAFC;
  --text-700: #E2E8F0;
  --text-500: #94A3B8;
}

/* Token-backed utility classes (no framework dependency) */
.app-bg { background: var(--bg); color: var(--text-900); }
.header-bg { background: var(--primary-600); }
.surface { background: var(--surface); }
.border-app { border: 1px solid var(--border); }
.border-t-app { border-top: 1px solid var(--border); }
.muted-bg { background: var(--muted); }
.text-muted { color: var(--text-500); }
.text-strong { color: var(--text-900); }
.primary-wash { background: var(--primary-100); }
.success-wash { background: var(--success-100); }
.success-fill { background: var(--success-600); }
.active-primary { color: var(--primary-600); }

.btn-primary {
  background: var(--primary-600);
  color: #ffffff;
  border-radius: 0.75rem;
  padding: 0.75rem 1.25rem;
  font-weight: 600;
  width: 100%;
}
.btn-primary:hover { filter: brightness(0.98); }
.btn-primary:focus-visible { outline: 2px solid var(--primary-100); outline-offset: 2px; }

.btn-secondary {
  background: transparent;
  color: var(--primary-600);
  border: 2px solid var(--primary-600);
  border-radius: 0.75rem;
  padding: 0.6rem 1rem;
  font-weight: 600;
  width: 100%;
}
.btn-secondary:focus-visible { outline: 2px solid var(--primary-100); outline-offset: 2px; }

.btn-danger {
  background: var(--danger-600);
  color: #ffffff;
  border-radius: 0.75rem;
  padding: 0.6rem 1rem;
  font-weight: 600;
}
.btn-danger:focus-visible { outline: 2px solid var(--danger-100); outline-offset: 2px; }

/* List divider helper */
.divide-app > * + * { border-top: 1px solid var(--border); }
```

---

## 4) React Reference (TypeScript) – Minimal App Shell

> All comments are above the relevant lines. XML‑style summaries included for each component.

```tsx
import React, { useMemo, useState } from "react";

// <summary>
// Entry point component that applies light/dark theme via data attribute
// and renders the mobile-first layout with header, content, and bottom nav.
// </summary>
export default function MyFoodBudgetMobileFirstUI(): JSX.Element
{
  // Maintains the selected primary section in the bottom navigation.
  const [activePrimarySectionName, setActivePrimarySectionName] = useState<
    "Dashboard" | "Plan" | "Ingredients" | "Recipes" | "Budget"
  >("Dashboard");

  // Maintains current theme preference for preview purposes.
  const [isDarkThemeSelected, setIsDarkThemeSelected] = useState<boolean>(false);

  // Provides example dashboard metrics until backend integration is completed.
  const exampleDashboardMetrics = useMemo(() =>
  {
    return {
      currentMonthTotalSpendAmount: 1472.35,
      monthOverMonthSavingsPercentage: 8.4,
      mostExpensiveIngredientName: "Ribeye Steak",
      monthlyBudgetLimitAmount: 2000,
      recentActivityItems: [
        { id: 1, description: "Added ingredient: Eggs (12 ct)", when: "2h" },
        { id: 2, description: "Updated price: Milk 1L to 10.95", when: "6h" },
        { id: 3, description: "Created recipe: Chicken Curry", when: "Yesterday" }
      ] as Array<{ id: number; description: string; when: string }>,
      monthlyTrendValues: [220, 240, 380, 410, 320, 280, 260, 300, 340, 360, 380, 410]
    };
  }, []);

  // Produces a derived progress ratio for budget usage in the current month.
  const monthlyBudgetUsageProgressRatio = useMemo<number>(() =>
  {
    const spend = exampleDashboardMetrics.currentMonthTotalSpendAmount;
    const budget = exampleDashboardMetrics.monthlyBudgetLimitAmount;
    if (budget <= 0) { return 0; }
    return Math.min(1, Math.max(0, spend / budget));
  }, [exampleDashboardMetrics]);

  // Renders the application container and child sections.
  return (
    <div data-theme={isDarkThemeSelected ? "dark" : "light"} className="min-h-screen flex flex-col app-bg">
      <AppHeader
        isDarkThemeSelected={isDarkThemeSelected}
        onToggleTheme={() => setIsDarkThemeSelected(v => !v)}
      />

      <main className="flex-1 overflow-y-auto pb-28 px-4" aria-live="polite">
        {activePrimarySectionName === "Dashboard" && (
          <DashboardOverviewSection
            currentMonthTotalSpendAmount={exampleDashboardMetrics.currentMonthTotalSpendAmount}
            monthOverMonthSavingsPercentage={exampleDashboardMetrics.monthOverMonthSavingsPercentage}
            mostExpensiveIngredientName={exampleDashboardMetrics.mostExpensiveIngredientName}
            monthlyBudgetLimitAmount={exampleDashboardMetrics.monthlyBudgetLimitAmount}
            monthlyBudgetUsageProgressRatio={monthlyBudgetUsageProgressRatio}
            recentActivityItems={exampleDashboardMetrics.recentActivityItems}
            monthlyTrendValues={exampleDashboardMetrics.monthlyTrendValues}
          />
        )}
        {activePrimarySectionName === "Plan" && (<WeeklyMealPlannerStub />)}
        {activePrimarySectionName === "Ingredients" && (<IngredientsGridSection />)}
        {activePrimarySectionName === "Recipes" && (<RecipesListSection />)}
        {activePrimarySectionName === "Budget" && (<BudgetAnalysisPreviewSection monthlyTrendValues={exampleDashboardMetrics.monthlyTrendValues} />)}
      </main>

      <AddPrimaryActionFloatingButton />

      <MobileBottomNavigation
        activePrimarySectionName={activePrimarySectionName}
        onPrimarySectionChange={setActivePrimarySectionName}
      />
    </div>
  );
}

// <summary>
// Application header with product title and a theme toggle button.
// </summary>
export function AppHeader(props: {
  isDarkThemeSelected: boolean;
  onToggleTheme: () => void;
}): JSX.Element
{
  // Derives an accessible label for the theme toggle.
  const toggleLabel = props.isDarkThemeSelected ? "Switch to Light Mode" : "Switch to Dark Mode";

  // Renders the header bar.
  return (
    <header className="sticky top-0 z-40 header-bg text-white shadow-md">
      <div className="max-w-screen-md mx-auto px-4 py-3 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">MyFoodBudget</h1>
          <p className="text-sm opacity-90">Track spending, plan meals, keep nutrition accountable.</p>
        </div>
        <button
          className="ml-4 btn-secondary whitespace-nowrap"
          aria-label={toggleLabel}
          onClick={props.onToggleTheme}
        >
          {props.isDarkThemeSelected ? "Light Mode" : "Dark Mode"}
        </button>
      </div>
    </header>
  );
}

// <summary>
// Dashboard section with key metrics, budget progress, trend sparkline, and recent activity.
// </summary>
export function DashboardOverviewSection(props: {
  currentMonthTotalSpendAmount: number;
  monthOverMonthSavingsPercentage: number;
  mostExpensiveIngredientName: string;
  monthlyBudgetLimitAmount: number;
  monthlyBudgetUsageProgressRatio: number;
  recentActivityItems: Array<{ id: number; description: string; when: string }>;
  monthlyTrendValues: number[];
}): JSX.Element
{
  // Renders the section content.
  return (
    <section className="max-w-screen-md mx-auto mt-4 space-y-4" aria-label="Dashboard Overview">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <KeyMetricCard
          titleText="This Month's Spend"
          primaryValueText={`DKK ${props.currentMonthTotalSpendAmount.toFixed(2)}`}
          supportingInfoText={`Budget: DKK ${props.monthlyBudgetLimitAmount.toFixed(0)}`}
        />
        <KeyMetricCard
          titleText="Savings vs Last Month"
          primaryValueText={`${props.monthOverMonthSavingsPercentage.toFixed(1)}%`}
          supportingInfoText="Positive is better"
        />
        <KeyMetricCard
          titleText="Top Cost Ingredient"
          primaryValueText={props.mostExpensiveIngredientName}
          supportingInfoText="Monitor price fluctuations"
        />
      </div>

      <div className="surface border-app rounded-2xl shadow p-4" aria-label="Budget Status">
        <h2 className="text-base font-semibold mb-2">Monthly Budget Status</h2>
        <MonthlyBudgetProgressBar progressRatio={props.monthlyBudgetUsageProgressRatio} />
        <div className="mt-3">
          <CompactLineSparkline values={props.monthlyTrendValues} />
        </div>
      </div>

      <div className="surface border-app rounded-2xl shadow p-4" aria-label="Recent Activity">
        <h2 className="text-base font-semibold mb-3">Recent Activity</h2>
        <RecentActivityList recentActivityItems={props.recentActivityItems} />
      </div>

      <QuickActionBar />
    </section>
  );
}

// <summary>
// Small reusable metric card used on the dashboard.
// </summary>
export function KeyMetricCard(props: {
  titleText: string;
  primaryValueText: string;
  supportingInfoText?: string;
}): JSX.Element
{
  // Renders the metric card.
  return (
    <div className="surface border-app rounded-2xl shadow p-4">
      <p className="text-sm text-muted">{props.titleText}</p>
      <p className="mt-1 text-xl font-semibold">{props.primaryValueText}</p>
      {props.supportingInfoText && (<p className="mt-1 text-sm text-muted">{props.supportingInfoText}</p>)}
    </div>
  );
}

// <summary>
// Budget progress indicator with semantic success color and accessible labels.
// </summary>
export function MonthlyBudgetProgressBar(props: { progressRatio: number }): JSX.Element
{
  // Computes width style for the filled portion of the progress bar.
  const widthPercentageStyle = { width: `${Math.round(props.progressRatio * 100)}%` } as const;

  // Renders the progress bar.
  return (
    <div>
      <div className="w-full h-3 muted-bg rounded-full overflow-hidden" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(props.progressRatio * 100)} aria-label="Budget Usage Progress">
        <div className="h-full success-fill" style={widthPercentageStyle} />
      </div>
      <p className="mt-1 text-xs text-muted">{Math.round(props.progressRatio * 100)}% of monthly budget used</p>
    </div>
  );
}

// <summary>
// Inline sparkline SVG for trend visualization. Minimal dependency footprint.
// </summary>
export function CompactLineSparkline(props: { values: number[] }): JSX.Element
{
  // Normalizes the data to [0,1] and builds a polyline.
  const max = Math.max(...props.values);
  const min = Math.min(...props.values);
  const normalizedPoints = props.values.map((v) => (v - min) / Math.max(1, (max - min)));
  const stepX = 100 / Math.max(1, props.values.length - 1);
  const points = normalizedPoints.map((n, i) => `${i * stepX},${100 - n * 100}`).join(" ");

  // Renders the SVG.
  return (
    <svg viewBox="0 0 100 100" className="w-full h-16" role="img" aria-label="Monthly Spending Trend">
      <polyline points={points} fill="none" stroke="var(--primary-600)" strokeWidth="2" />
    </svg>
  );
}

// <summary>
// Activity list used on the dashboard to show recent user actions.
// </summary>
export function RecentActivityList(props: { recentActivityItems: Array<{ id: number; description: string; when: string }> }): JSX.Element
{
  // Renders list items separated by tokenized dividers.
  return (
    <ul className="divide-app">
      {props.recentActivityItems.map((item) => (
        <li key={item.id} className="py-2">
          <p className="text-sm font-medium">{item.description}</p>
          <p className="text-xs text-muted mt-0.5">{item.when}</p>
        </li>
      ))}
    </ul>
  );
}

// <summary>
// Quick action buttons component to reduce taps for frequent tasks.
// </summary>
export function QuickActionBar(): JSX.Element
{
  // Renders a 2x/4x responsive grid of common actions.
  return (
    <div className="surface border-app rounded-2xl shadow p-4">
      <h2 className="text	base font-semibold mb-2">Quick Actions</h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <button className="btn-primary" aria-label="Add Ingredient Now">Add Ingredient</button>
        <button className="btn-secondary" aria-label="Create New Recipe">Create Recipe</button>
        <button className="btn-secondary" aria-label="Plan This Week">Plan Week</button>
        <button className="btn-secondary" aria-label="View Budget Dashboard">View Budget</button>
      </div>
    </div>
  );
}

// <summary>
// Ingredients section with search bar and card grid.
// </summary>
export function IngredientsGridSection(): JSX.Element
{
  // Maintains the search query for client-side filtering.
  const [searchQueryText, setSearchQueryText] = useState<string>("");

  // Example ingredient cards; replace with server data.
  const exampleIngredientCards = [
    { id: 1, name: "Chicken Breast", brand: "Generic", quantity: "1 kg", price: 69.95, pricePerUnit: "69.95/kg" },
    { id: 2, name: "Rice", brand: "Basmatica", quantity: "2 kg", price: 39.5, pricePerUnit: "19.75/kg" },
    { id: 3, name: "Greek Yogurt", brand: "Farm Fresh", quantity: "1 kg", price: 24.95, pricePerUnit: "24.95/kg" },
    { id: 4, name: "Olive Oil", brand: "Primavera", quantity: "1 L", price: 59.0, pricePerUnit: "59.00/L" }
  ] as const;

  // Computes the filtered list based on the query.
  const filteredCards = exampleIngredientCards.filter((c) =>
    `${c.name} ${c.brand}`.toLowerCase().includes(searchQueryText.toLowerCase())
  );

  // Renders the section.
  return (
    <section className="max-w-screen-md mx-auto mt-4 space-y-4" aria-label="Ingredients">
      <SearchAndFilterBar searchQueryText={searchQueryText} onSearchQueryTextChange={setSearchQueryText} />

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {filteredCards.map((card) => (
          <IngredientCard
            key={card.id}
            ingredientName={card.name}
            ingredientBrandName={card.brand}
            displayQuantityText={card.quantity}
            displayPriceText={`DKK ${card.price.toFixed(2)}`}
            displayPricePerUnitText={card.pricePerUnit}
          />
        ))}
      </div>
    </section>
  );
}

// <summary>
// Search bar for ingredients with focus ring mapped to primary tokens.
// </summary>
export function SearchAndFilterBar(props: { searchQueryText: string; onSearchQueryTextChange: (v: string) => void; }): JSX.Element
{
  // Renders the label and input.
  return (
    <div className="surface border-app rounded-2xl shadow p-4">
      <label className="block text-sm font-medium text-strong" htmlFor="ingredient-search-input">Search Ingredients</label>
      <input
        id="ingredient-search-input"
        type="search"
        placeholder="Type a name or brand"
        value={props.searchQueryText}
        onChange={(e) => props.onSearchQueryTextChange(e.target.value)}
        className="mt-1 w-full rounded-xl px-3 py-2 focus:outline-none focus:ring-2"
        style={{ border: "1px solid var(--border)", boxShadow: "0 0 0 2px transparent" }}
        onFocus={(e) => (e.currentTarget.style.boxShadow = "0 0 0 2px var(--primary-100)")}
        onBlur={(e) => (e.currentTarget.style.boxShadow = "0 0 0 2px transparent")}
      />
    </div>
  );
}

// <summary>
// Ingredient card with quantity, price, and per-unit info, using semantic washes.
// </summary>
export function IngredientCard(props: {
  ingredientName: string;
  ingredientBrandName: string;
  displayQuantityText: string;
  displayPriceText: string;
  displayPricePerUnitText: string;
}): JSX.Element
{
  // Renders the card.
  return (
    <article className="surface border-app rounded-2xl shadow p-4">
      <h3 className="text-base font-semibold">{props.ingredientName}</h3>
      <p className="text-sm text-muted mt-0.5">{props.ingredientBrandName}</p>
      <div className="mt-3 grid grid-cols-3 gap-2 text-sm">
        <div className="muted-bg rounded-xl p-2 text-center">
          <p className="font-medium">Quantity</p>
          <p className="text-muted">{props.displayQuantityText}</p>
        </div>
        <div className="success-wash rounded-xl p-2 text-center">
          <p className="font-medium">Price</p>
          <p className="text-strong">{props.displayPriceText}</p>
        </div>
        <div className="primary-wash rounded-xl p-2 text-center">
          <p className="font-medium">Per Unit</p>
          <p className="text-muted">{props.displayPricePerUnitText}</p>
        </div>
      </div>
      <div className="mt-4 flex gap-2">
        <button className="btn-secondary">Edit</button>
        <button className="btn-danger">Delete</button>
      </div>
    </article>
  );
}

// <summary>
// Weekly planner stub to validate layout and touch ergonomics.
// </summary>
export function WeeklyMealPlannerStub(): JSX.Element
{
  // Defines day labels.
  const days: ReadonlyArray<string> = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  // Renders a simple grid.
  return (
    <section className="max-w-screen-md mx-auto mt-4 space-y-4" aria-label="Weekly Meal Planner">
      <div className="surface border-app rounded-2xl shadow p-4">
        <h2 className="text-base font-semibold mb-2">Plan This Week</h2>
        <div className="grid grid-cols-7 gap-1 text-center text-sm">
          {days.map((d) => (
            <div key={d} className="muted-bg rounded-lg py-2">
              <p className="font-medium">{d}</p>
              <p className="text-xs text-muted">Add Meal</p>
            </div>
          ))}
        </div>
      </div>

      <div className="surface border-app rounded-2xl shadow p-4">
        <h3 className="text-sm font-semibold mb-2">Suggested Recipes</h3>
        <p className="text-sm text-muted">Suggestions will appear here based on cost and nutrition once connected.</p>
      </div>
    </section>
  );
}

// <summary>
// Recipes list section with cost and kcal metadata text.
// </summary>
export function RecipesListSection(): JSX.Element
{
  // Example items; replace with server data.
  const exampleRecipes = [
    { id: 1, name: "Chicken Curry", cost: 42.5, caloriesPerServing: 520 },
    { id: 2, name: "Beef Stir Fry", cost: 38.2, caloriesPerServing: 480 },
    { id: 3, name: "Vegetable Soup", cost: 18.4, caloriesPerServing: 220 }
  ] as const;

  // Renders the list.
  return (
    <section className="max-w-screen-md mx

```
