import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./hooks/useTheme";
import { Layout } from "./components/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import { ProjectsPage } from "./pages/ProjectsPage";
import { ProjectDetailPage } from "./pages/ProjectDetailPage";
import { CharactersPage } from "./pages/CharactersPage";
import { ChaptersPage } from "./pages/ChaptersPage";
import { StoryBiblePage } from "./pages/StoryBiblePage";
import { DailyWriterPage } from "./pages/DailyWriterPage";
import { ReferenceNovelPage } from "./pages/ReferenceNovelPage";
import { AISettingsPage } from "./pages/AISettingsPage";

export default function App() {
  const basename = window.location.pathname.startsWith("/app") ? "/app" : undefined;

  return (
    <ThemeProvider>
      <BrowserRouter basename={basename}>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<DashboardPage />} />
            <Route path="projects" element={<ProjectsPage />} />
            <Route path="projects/:projectId" element={<ProjectDetailPage />} />
            <Route path="characters" element={<CharactersPage />} />
            <Route path="chapters" element={<ChaptersPage />} />
            <Route path="story-bible" element={<StoryBiblePage />} />
            <Route path="daily-writer" element={<DailyWriterPage />} />
            <Route path="reference-novels" element={<ReferenceNovelPage />} />
            <Route path="model-settings" element={<AISettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
