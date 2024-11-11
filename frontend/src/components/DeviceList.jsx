import React from "react";
import { Badge } from "./ui/badge";
import { Skeleton } from "./ui/skeleton";

export const DeviceList = ({ devices, loading }) => {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="p-4 border rounded-lg">
            <Skeleton className="h-4 w-1/3 mb-2" />
            <Skeleton className="h-4 w-2/3" />
          </div>
        ))}
      </div>
    );
  }

  if (!devices.length) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No devices found. Click "Scan Network" to start scanning.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {devices.map((device, index) => (
        <div
          key={index}
          className="p-4 border rounded-lg hover:bg-accent transition-colors"
        >
          <div className="flex justify-between items-start">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-medium">{device.ip}</h3>
                <Badge variant="outline">{device.type}</Badge>
              </div>
              <p className="text-sm text-muted-foreground">MAC: {device.mac}</p>
              {device.vendor && (
                <p className="text-sm text-muted-foreground">
                  Vendor: {device.vendor}
                </p>
              )}
            </div>
            <div className="h-3 w-3 rounded-full bg-green-500" />
          </div>
        </div>
      ))}
    </div>
  );
};
