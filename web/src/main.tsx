import { StrictMode } from "react"
import { createRoot } from "react-dom/client"

import { ThemeProvider } from "@/components/theme-provider"
import { I18nProvider } from "@/lib/i18n"
import { StudioProvider } from "@/lib/studio"

import App from "./App.tsx"
import "./index.css"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <I18nProvider>
        <StudioProvider>
          <App />
        </StudioProvider>
      </I18nProvider>
    </ThemeProvider>
  </StrictMode>,
)
