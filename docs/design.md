# Interface decisions

The existing app was a single column with configuration, all FAQs, and chat competing for attention. This redesign keeps the assignment's Python and Streamlit stack and places the conversation first.

Direction: a dark knowledge workspace with charcoal surfaces, a mint accent, clear typography, and consistent rounded corners. The welcome view emphasizes the conversation with a typographic brand mark and larger headline. Suggested questions include short descriptions, while the active navigation item has a clear selected state. Native Streamlit controls and local system fonts keep the interface lightweight. No external fonts, decorative photos, or animation dependencies are needed for this task.

The UI/UX search matched FAQ/documentation navigation and minimal layouts. Its suggested typography was not needed; the app keeps fast local fonts. Marketing-page rules from the frontend design skill apply only where relevant to the title, spacing, colors, and responsive structure.

Chat contains actionable suggested questions, explicit answer modes, source expanders, and loading and failure states. FAQ library provides search and topics. Project guide explains usage and the submission steps. Suggestions stack vertically below 640 pixels, and native controls retain labels and keyboard support. Reduced-motion preferences disable transitions.

Desktop and phone screenshots were reviewed using a local headless Edge browser. Overflow checks passed at 375, 768, and 1024 pixel widths, with reduced motion enabled. Screenshots are saved locally under `.tmp/screenshots`. All 20 automated tests passed. The app has one consistent dark theme; restart Streamlit after changing theme configuration to apply it to an existing server.
