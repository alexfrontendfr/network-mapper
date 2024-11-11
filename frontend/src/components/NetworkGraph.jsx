import React, { useEffect, useRef } from "react";
import { Card } from "./ui/card";

export const NetworkGraph = ({ devices }) => {
  const graphRef = useRef(null);

  useEffect(() => {
    const loadGraph = async () => {
      try {
        const response = await fetch("http://localhost:5000/api/graph");
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        if (graphRef.current) {
          graphRef.current.src = url;
        }
        return () => URL.revokeObjectURL(url);
      } catch (error) {
        console.error("Failed to load graph:", error);
      }
    };

    if (devices.length > 0) {
      loadGraph();
    }
  }, [devices]);

  if (!devices.length) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No network data available. Perform a scan to view the network graph.
      </div>
    );
  }

  return (
    <Card className="p-4">
      <img
        ref={graphRef}
        alt="Network Graph"
        className="w-full h-auto"
        style={{ minHeight: "400px" }}
      />
    </Card>
  );
};
