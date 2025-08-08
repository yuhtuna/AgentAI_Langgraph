import * as Location from "expo-location";
import type React from "react";
import { useCallback, useEffect, useState } from "react";
import { StyleSheet, Text, View, type ViewStyle } from "react-native";

interface LocationDisplayProps {
  style?: ViewStyle;
}

interface LocationData {
  latitude: number;
  longitude: number;
  accuracy: number | null;
  address?: string;
}

const LocationDisplay: React.FC<LocationDisplayProps> = ({ style }) => {
  const [location, setLocation] = useState<LocationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const getLocation = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Request permissions
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        setError("Location permission denied");
        setLoading(false);
        return;
      }

      // Get current position
      const currentLocation = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });

      const locationData: LocationData = {
        latitude: currentLocation.coords.latitude,
        longitude: currentLocation.coords.longitude,
        accuracy: currentLocation.coords.accuracy,
      };

      // Try to get address (reverse geocoding)
      try {
        const addressResponse = await Location.reverseGeocodeAsync({
          latitude: currentLocation.coords.latitude,
          longitude: currentLocation.coords.longitude,
        });

        if (addressResponse.length > 0) {
          const addr = addressResponse[0];
          locationData.address =
            `${addr.street || ""} ${addr.city || ""}, ${addr.region || ""} ${addr.postalCode || ""}`.trim();
        }
      } catch (geocodeError) {
        console.log("Geocoding failed:", geocodeError);
        // Continue without address
      }

      setLocation(locationData);
    } catch (locationError) {
      console.error("Location error:", locationError);
      setError("Failed to get location");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    getLocation();
  }, [getLocation]);

  const formatCoordinate = (coord: number) => {
    return coord.toFixed(6);
  };

  if (loading) {
    return (
      <View style={[styles.container, style]}>
        <Text style={styles.loadingText}>Getting location...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={[styles.container, style]}>
        <Text style={styles.errorText}>📍 {error}</Text>
      </View>
    );
  }

  if (!location) {
    return (
      <View style={[styles.container, style]}>
        <Text style={styles.errorText}>📍 Location unavailable</Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, style]}>
      <Text style={styles.title}>📍 Current Location</Text>
      <Text style={styles.coordinates}>
        {formatCoordinate(location.latitude)},{" "}
        {formatCoordinate(location.longitude)}
      </Text>
      {location.address && (
        <Text style={styles.address} numberOfLines={2}>
          {location.address}
        </Text>
      )}
      {location.accuracy && (
        <Text style={styles.accuracy}>
          Accuracy: ±{Math.round(location.accuracy)}m
        </Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#f8f9fa",
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e9ecef",
    marginVertical: 4,
  },
  title: {
    fontSize: 14,
    fontWeight: "600",
    color: "#0D87E1",
    marginBottom: 4,
    fontFamily: "SemiBold",
  },
  coordinates: {
    fontSize: 13,
    fontFamily: "Medium",
    color: "#495057",
    marginBottom: 2,
  },
  address: {
    fontSize: 12,
    fontFamily: "Regular",
    color: "#6c757d",
    marginBottom: 2,
    lineHeight: 16,
  },
  accuracy: {
    fontSize: 11,
    fontFamily: "Regular",
    color: "#9ca3af",
  },
  loadingText: {
    fontSize: 13,
    fontFamily: "Medium",
    color: "#6c757d",
    textAlign: "center",
  },
  errorText: {
    fontSize: 13,
    fontFamily: "Medium",
    color: "#dc3545",
    textAlign: "center",
  },
});

export default LocationDisplay;
