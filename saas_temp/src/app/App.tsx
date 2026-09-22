import { RouterProvider } from "react-router";
import { router } from "./routes";
import { AIAssistant } from "./components/AIAssistant";

export default function App() {
  return (
    <>
      <RouterProvider router={router} />
      <AIAssistant />
    </>
  );
}
