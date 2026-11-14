import { createBrowserRouter } from "react-router-dom";
import PublicLayout from "./layouts/PublicLayout";
import AppLayout from "./layouts/AppLayout";
import Home from "@/pages/Home";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import Dashboard from "@/pages/Dashboard";
import Humanize from "@/pages/Humanize";
import History from "@/pages/History";
import JobDetail from "@/pages/JobDetail";
import Profile from "@/pages/Profile";
import Team from "@/pages/Team";
import Admin from "@/pages/Admin";
import NotFound from "@/pages/NotFound";
import Studio from "@/pages/Studio";
import Gallery from "@/pages/Gallery";
import Generate from "@/pages/Generate";
import Hours from "@/pages/Hours";

export const router = createBrowserRouter([
  { element: <PublicLayout />, children: [{ path: "/", element: <Home /> }] },
  { path: "/login", element: <Login /> },
  { path: "/registro", element: <Register /> },
  {
    path: "/app",
    element: <AppLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "humanizar", element: <Humanize /> },
      { path: "estudio", element: <Studio /> },
      { path: "galeria", element: <Gallery /> },
      { path: "generar", element: <Generate /> },
      { path: "horas", element: <Hours /> },
      { path: "historial", element: <History /> },
      { path: "trabajos/:id", element: <JobDetail /> },
      { path: "perfil", element: <Profile /> },
      { path: "equipo", element: <Team /> },
      { path: "admin", element: <Admin /> },
      { path: "*", element: <NotFound /> },
    ],
  },
  { path: "*", element: <NotFound /> },
]);
