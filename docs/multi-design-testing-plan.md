# Multi-Design Testing System Implementation Plan

## Overview
Create a dynamic UI testing system with 3 design variants + dark mode toggle accessible via buttons in the top-right header area. Users can switch between designs in real-time for comparative testing.

## Design Variants to Implement

### Button 1: "Legacy Design" 
- **Preserve existing styles** as baseline reference
- **Keep current Bootstrap-heavy approach** 
- **Maintain existing color scheme** and layout patterns

### Button 2: "Current Design"
- **Your existing modern CSS variables** (from current styles.css)
- **Current card system** and spacing
- **Existing mobile responsiveness**

### Button 3: "New Mobile-First Design"
- **Implement the new design tokens** from docs/new-UI-design.md
- **Mobile-first layout patterns** (bottom nav, floating buttons, card grids)
- **Semantic color system** (calm blue/green trust palette)

### Dark Mode Toggle
- **Works across all 3 designs** with appropriate dark variants
- **Persistent user preference** via localStorage/session

## Technical Implementation

### 1. CSS Architecture
```
/static/css/
├── design-legacy.css     # Original styles
├── design-current.css    # Current modern styles  
├── design-mobile.css     # New mobile-first design
├── themes-dark.css       # Dark mode overrides for all
└── design-switcher.js    # Theme switching logic
```

### 2. Header Controls
- **Add 4 buttons in top-right**: [1] [2] [3] [🌙]
- **Visual active state** showing current selection
- **Smooth transitions** between design switches
- **Responsive button layout** for mobile

### 3. State Management
- **Use data attributes** on `<body>` tag: `data-design="1|2|3"` and `data-theme="light|dark"`
- **Session storage** for persistence across pages
- **URL parameter support** for sharing specific design versions

### 4. Testing Benefits
- **Real-time comparison** by users without developer presence
- **Single deployment** serving all variants
- **Easy user feedback collection** with design context
- **A/B/C testing metrics** possible with analytics

## Implementation Steps

1. **Save current styles.css as design-current.css**
2. **Create design-legacy.css** with basic Bootstrap styling
3. **Create design-mobile.css** implementing the new mobile-first specs
4. **Add design switcher controls** to layout.html header
5. **Implement JavaScript switching logic** with persistence
6. **Add dark mode support** for all three designs
7. **Test across all pages** and design combinations

## Expected Outcome
A powerful testing platform where users can experience all design variants seamlessly and provide comparative feedback without requiring developer presence or separate deployments.