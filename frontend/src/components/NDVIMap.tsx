import { useEffect, useRef } from "react";

interface Props {
  fieldPolygon?: any;
  ndviValue?: number;
  onMapClick?: (lat: number, lng: number) => void;
  drawMode?: boolean;
  drawPoints?: [number, number][];
}

export default function NDVIMap({ fieldPolygon, ndviValue, onMapClick, drawMode, drawPoints }: Props) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const layerRef = useRef<any>(null);
  const drawLayerRef = useRef<any>(null);
  const markerLayerRef = useRef<any>(null);

  useEffect(() => {
    import("leaflet").then((L) => {
      if (!mapRef.current) return;
      if (mapInstanceRef.current) return;

      const map = L.map(mapRef.current).setView([39.0, 35.0], 6);

      // Satellite tile layer (Esri World Imagery)
      L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        {
          attribution: "Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics",
          maxZoom: 19,
        }
      ).addTo(map);

      // Labels overlay
      L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        { maxZoom: 19, opacity: 0.7 }
      ).addTo(map);

      mapInstanceRef.current = map;
    });

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Map click handler for draw mode
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    const handler = (e: any) => {
      if (onMapClick && drawMode) {
        onMapClick(e.latlng.lat, e.latlng.lng);
      }
    };

    map.on("click", handler);
    return () => { map.off("click", handler); };
  }, [onMapClick, drawMode]);

  // Draw points preview
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    import("leaflet").then((L) => {
      const map = mapInstanceRef.current;

      if (drawLayerRef.current) { map.removeLayer(drawLayerRef.current); drawLayerRef.current = null; }
      if (markerLayerRef.current) { map.removeLayer(markerLayerRef.current); markerLayerRef.current = null; }

      if (drawPoints && drawPoints.length > 0) {
        const markers = L.layerGroup();
        drawPoints.forEach((p, i) => {
          L.circleMarker([p[0], p[1]], {
            radius: 6, color: "#facc15", fillColor: "#facc15", fillOpacity: 0.9, weight: 2,
          }).bindTooltip(`${i + 1}`, { permanent: true, direction: "top", className: "text-xs font-bold" }).addTo(markers);
        });
        markers.addTo(map);
        markerLayerRef.current = markers;

        if (drawPoints.length >= 3) {
          const latlngs = drawPoints.map((p) => [p[0], p[1]] as [number, number]);
          const polygon = L.polygon(latlngs, {
            color: "#facc15", weight: 2, fillOpacity: 0.2, fillColor: "#facc15", dashArray: "6,4",
          }).addTo(map);
          drawLayerRef.current = polygon;
        }
      }
    });
  }, [drawPoints]);

  useEffect(() => {
    if (!mapInstanceRef.current) return;

    import("leaflet").then((L) => {
      const map = mapInstanceRef.current;

      if (layerRef.current) {
        map.removeLayer(layerRef.current);
        layerRef.current = null;
      }

      if (fieldPolygon) {
        const ndviColor = ndviValue
          ? ndviValue > 0.6
            ? "#2d6a4f"
            : ndviValue > 0.4
            ? "#52b788"
            : ndviValue > 0.2
            ? "#f4a261"
            : "#e76f51"
          : "#3b82f6";

        const geoLayer = L.geoJSON(fieldPolygon, {
          style: {
            color: ndviColor,
            weight: 3,
            fillOpacity: 0.35,
            fillColor: ndviColor,
          },
        }).addTo(map);

        layerRef.current = geoLayer;
        map.fitBounds(geoLayer.getBounds(), { padding: [30, 30] });
      }
    });
  }, [fieldPolygon, ndviValue]);

  return (
    <div className="relative w-full h-full">
      <div ref={mapRef} className="w-full h-full rounded-xl z-0" />
      {drawMode && (
        <div className="absolute top-3 left-3 bg-yellow-500/90 backdrop-blur-sm px-3 py-2 rounded-lg shadow z-[1000] text-sm text-white font-medium">
          Haritaya tıklayarak köşe noktalarını seçin (min 3)
        </div>
      )}
      {ndviValue !== undefined && (
        <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm px-3 py-2 rounded-lg shadow z-[1000] text-sm">
          <span className="text-gray-500">NDVI:</span>{" "}
          <span
            className={`font-bold ${
              ndviValue > 0.6
                ? "text-green-700"
                : ndviValue > 0.4
                ? "text-green-500"
                : ndviValue > 0.2
                ? "text-orange-500"
                : "text-red-500"
            }`}
          >
            {ndviValue.toFixed(3)}
          </span>
        </div>
      )}
      {!fieldPolygon && !drawMode && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-50/70 rounded-xl z-[500]">
          <p className="text-gray-400 text-sm">Haritada görmek için bir tarla seçin</p>
        </div>
      )}
    </div>
  );
}
