import React from "react";
import NetworkMapper from "./components/NetworkMapper";
import { ThemeProvider } from "./components/theme-provider";

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="network-mapper-theme">
      <div className="min-h-screen bg-background">
        <NetworkMapper />
      </div>
    </ThemeProvider>
  );
}

export default App;
