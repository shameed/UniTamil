# Design Standards (Unitamil)

Adapted from Inspire Design System for Flet/Python.

## 1. Colors (Token Map)

| Token            | Hex       | Flet Constant          | Usage                                |
| :--------------- | :-------- | :--------------------- | :----------------------------------- |
| `primary`        | `#007BFF` | `colors.BLUE`          | Primary Actions, Progress Bar, Links |
| `sidebar`        | `#0F172A` | `colors.BLUE_GREY_900` | Sidebar Background                   |
| `sidebar-text`   | `#FFFFFF` | `colors.WHITE`         | Sidebar Text                         |
| `background`     | `#F1F5F9` | `colors.BLUE_GREY_50`  | Main Content Background              |
| `surface`        | `#FFFFFF` | `colors.WHITE`         | Card backgrounds                     |
| `text-primary`   | `#1E293B` | `colors.BLUE_GREY_900` | Main text (Content)                  |
| `text-secondary` | `#64748B` | `colors.BLUE_GREY_500` | Subtitles, hints                     |
| `success`        | `#22C55E` | `colors.GREEN_500`     | Success states                       |

## 2. Typography

- **Header 1**: Size 24, Weight BOLD, Color `text-primary` (Content) or `sidebar-text` (Sidebar).
- **Header 2**: Size 18, Weight SEMI_BOLD, Color `text-primary`.
- **Body**: Size 14, Weight NORMAL, Color `text-primary`.
- **Label**: Size 12, Weight BOLD, Color `sidebar-text` (Sidebar Labels).

## 3. Layout Grid

- **Sidebar**: Fixed Width (e.g., 300px), Full Height.
- **Content**: Flexible Width, Scrollable.
- **Padding**: 20px (Global).

## 4. Components

### File Progress Card

- **Bg**: `surface` (White)
- **Radius**: 8
- **Padding**: 15
- **Shadow**: Small (Elevation 1)
- **Elements**: Filename (H2), Progress Bar (Primary), Status Text (Secondary).

### Inputs (Sidebar)

- **Style**: White text on Dark background (or light inputs if contrast needed).
- **Buttons**: Full width, outlined or filled.
