import React, { useState, useEffect } from "react";
import { Card, CardHeader, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { Alert, AlertDescription } from "./ui/alert";
import {
  RefreshCw,
  Download,
  AlertCircle,
  List,
  Network,
  Moon,
  Sun,
} from "lucide-react";
import { DeviceList } from "./DeviceList";
import { NetworkGraph } from "./NetworkGraph";
import { format } from "date-fns";
import { useTheme } from "./theme-provider";

const NetworkMapper = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastScan, setLastScan] = useState(null);
  const [activeView, setActiveView] = useState("list");
  const { theme, setTheme } = useTheme();

  const handleError = (error) => {
    console.error("Error:", error);
    setError(error.message || "An error occurred during the scan");
    setLoading(false);
  };

  const scanNetwork = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("http://localhost:5000/api/scan");
      if (!response.ok) {
        const data = await response.json();
        throw new Error(
          data.error || `Network scan failed with status: ${response.status}`
        );
      }
      const data = await response.json();
      if (Array.isArray(data) && data.length > 0) {
        setDevices(data);
        setLastScan(new Date());
      } else {
        setDevices([]);
        setError("No devices found on the network");
      }
    } catch (error) {
      handleError(error);
    } finally {
      setLoading(false);
    }
  };

  const downloadGraph = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/graph");
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "Failed to download network map");
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `network-map-${format(new Date(), "yyyy-MM-dd-HH-mm")}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      handleError(error);
    }
  };

  return (
    <div className="min-h-screen bg-background pt-8 pb-8">
      <div className="container mx-auto p-4 max-w-6xl">
        <Card className="shadow-lg">
          <CardHeader className="border-b">
            <div className="flex flex-col space-y-4">
              <div className="flex justify-between items-center">
                <div className="flex items-center space-x-4">
                  <Network className="h-8 w-8 text-primary" />
                  <div>
                    <h1 className="text-3xl font-bold">Network Mapper</h1>
                    {lastScan && (
                      <p className="text-sm text-muted-foreground">
                        Last scan: {format(lastScan, "PPpp")}
                      </p>
                    )}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                >
                  {theme === "dark" ? (
                    <Sun className="h-5 w-5" />
                  ) : (
                    <Moon className="h-5 w-5" />
                  )}
                </Button>
              </div>
              <div className="flex flex-wrap gap-2 justify-between items-center">
                <div className="flex flex-wrap gap-2">
                  <Button
                    onClick={() => setActiveView("list")}
                    variant={activeView === "list" ? "default" : "outline"}
                    className="flex items-center gap-2"
                  >
                    <List className="h-4 w-4" />
                    List View
                  </Button>
                  <Button
                    onClick={() => setActiveView("graph")}
                    variant={activeView === "graph" ? "default" : "outline"}
                    className="flex items-center gap-2"
                  >
                    <Network className="h-4 w-4" />
                    Graph View
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button
                    onClick={scanNetwork}
                    disabled={loading}
                    className="flex items-center gap-2"
                  >
                    <RefreshCw className={loading ? "animate-spin" : ""} />
                    Scan Network
                  </Button>
                  <Button
                    onClick={downloadGraph}
                    disabled={!devices.length || loading}
                    variant="outline"
                    className="flex items-center gap-2"
                  >
                    <Download />
                    Download Map
                  </Button>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-6">
            {error && (
              <Alert variant="destructive" className="mb-6">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="bg-card rounded-lg p-4">
              {activeView === "list" ? (
                <DeviceList devices={devices} loading={loading} />
              ) : (
                <NetworkGraph devices={devices} />
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default NetworkMapper;
