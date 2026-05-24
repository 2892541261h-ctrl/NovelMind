import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import { ProjectsPage } from "./pages/ProjectsPage";
import { ProjectDetailPage } from "./pages/ProjectDetailPage";
import { CharactersPage } from "./pages/CharactersPage";
import { ChaptersPage } from "./pages/ChaptersPage";
import { StoryBiblePage } from "./pages/StoryBiblePage";
import { ModelSettingsPage } from "./pages/ModelSettingsPage";
import { DailyWriterPage } from "./pages/DailyWriterPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="projects" element={<ProjectsPage />} />
          <Route path="projects/:projectId" element={<ProjectDetailPage />} />
          <Route path="characters" element={<CharactersPage />} />
          <Route path="chapters" element={<ChaptersPage />} />
          <Route path="story-bible" element={<StoryBiblePage />} />
          <Route path="model-settings" element={<ModelSettingsPage />} />
          <Route path="daily-writer" element={<DailyWriterPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
