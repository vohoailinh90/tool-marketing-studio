import { BrowserRouter, Route, Routes } from "react-router-dom"

import { AppLayout } from "@/components/layout/app-layout"
import { AnalysePage } from "@/pages/analyse"
import { GuidePage } from "@/pages/guide"
import { HistoryPage } from "@/pages/history"
import { InsightsPage } from "@/pages/insights"
import { OverviewPage } from "@/pages/overview"
import { PreviewPage } from "@/pages/preview"
import { PublishPage } from "@/pages/publish"
import { WritePage } from "@/pages/write"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<OverviewPage />} />
          <Route path="analyse" element={<AnalysePage />} />
          <Route path="write" element={<WritePage />} />
          <Route path="preview" element={<PreviewPage />} />
          <Route path="publish" element={<PublishPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="insights" element={<InsightsPage />} />
          <Route path="guide" element={<GuidePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
