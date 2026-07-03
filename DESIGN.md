---
name: Wine Cellar
description: A personal cellar shaped like a refined tasting notebook
colors:
  bordeaux: "#64283c"
  bordeaux-deep: "#3c1428"
  oxblood: "#642828"
  champagne: "#c8a064"
  sage: "#646450"
  ink: "#141414"
  charcoal: "#282828"
  cream: "#fffff0"
  blush: "#fff0f0"
  surface: "#ffffff"
  border: "#dcdcc8"
  muted: "#c8c8b4"
  info: "#3c8cf0"
typography:
  display:
    fontFamily: "Fraunces, Georgia, serif"
    fontSize: "3.75rem"
    fontWeight: 500
    lineHeight: 1
  title:
    fontFamily: "Fraunces, Georgia, serif"
    fontSize: "1.75rem"
    fontWeight: 500
    lineHeight: 1.15
  body:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.2
rounded:
  sm: "8px"
  md: "14px"
  lg: "22px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "40px"
components:
  button-primary:
    backgroundColor: "{colors.bordeaux}"
    textColor: "{colors.cream}"
    rounded: "{rounded.lg}"
    padding: "10px 18px"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
---

# Design System: Wine Cellar

## Overview

**Creative North Star: "Le carnet de dégustation personnel"**

The interface pairs the quiet authority of an editorial wine journal with efficient,
recognizable application controls. Bordeaux carries identity, champagne marks valuable
details, and near-neutral cream keeps long browsing sessions calm. The collection remains
visual and tactile while inventory actions stay direct.

It rejects generic admin dashboards, ornamental wine-shop clichés, neon SaaS styling,
and decoration that competes with bottle data.

## Colors

Bordeaux anchors navigation and primary actions; champagne highlights vintages and
ratings; sage supports secondary metadata; cream and true white separate canvas from data.
The supplied palette is preserved, but not every swatch must appear on every screen.

## Typography

**Display Font:** Fraunces (Georgia fallback)  
**Body Font:** Inter (system-ui fallback)

Fraunces is reserved for page and wine titles. Inter carries controls, labels, tables,
forms, and body text. Product labels never use the display face.

## Elevation

Surfaces are bordered by default. Soft ambient shadows are reserved for the hero,
floating navigation, and interactive cards; state and hierarchy should remain legible
without shadow.

## Components

Buttons use pill geometry only for compact actions; full-width form actions use the
14px control radius. Cards use 14–22px corners, a quiet border, and generous internal
spacing. Inputs use white surfaces, clear labels, and a bordeaux focus ring. Mobile
navigation prioritizes collection, add/scan, and account access.

## Do's and Don'ts

### Do:

- **Do** make bottle photography and wine names the strongest card elements.
- **Do** preserve 44px touch targets and visible keyboard focus.
- **Do** collapse filters behind a clear control on narrow screens.

### Don't:

- **Don't** resemble a generic Bootstrap admin or cold enterprise dashboard.
- **Don't** use neon gradients, glassmorphism, gradient text, or decorative motion.
- **Don't** hide operational stock actions behind purely decorative interactions.
