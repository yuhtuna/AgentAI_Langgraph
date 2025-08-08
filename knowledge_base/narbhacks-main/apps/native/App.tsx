import { useFonts } from "expo-font";
import { LogBox, Platform, StatusBar, View } from "react-native";
import ConvexClientProvider from "./ConvexClientProvider";
import LocationDisplay from "./src/components/LocationDisplay";
import Navigation from "./src/navigation/Navigation";

export default function App() {
  LogBox.ignoreLogs(["Warning: ..."]);
  LogBox.ignoreAllLogs();

  const [loaded] = useFonts({
    Bold: require("./src/assets/fonts/Inter-Bold.ttf"),
    SemiBold: require("./src/assets/fonts/Inter-SemiBold.ttf"),
    Medium: require("./src/assets/fonts/Inter-Medium.ttf"),
    Regular: require("./src/assets/fonts/Inter-Regular.ttf"),

    MBold: require("./src/assets/fonts/Montserrat-Bold.ttf"),
    MSemiBold: require("./src/assets/fonts/Montserrat-SemiBold.ttf"),
    MMedium: require("./src/assets/fonts/Montserrat-Medium.ttf"),
    MRegular: require("./src/assets/fonts/Montserrat-Regular.ttf"),
    MLight: require("./src/assets/fonts/Montserrat-Light.ttf"),
  });
  if (!loaded) {
    return false;
  }

  const STATUS_BAR_HEIGHT =
    Platform.OS === "ios" ? 50 : StatusBar.currentHeight;

  return (
    <ConvexClientProvider>
      <View style={{ flex: 1 }}>
        <View style={{ height: STATUS_BAR_HEIGHT, backgroundColor: "#0D87E1" }}>
          <StatusBar
            translucent
            backgroundColor={"#0D87E1"}
            barStyle="light-content"
          />
        </View>
        <LocationDisplay style={{ margin: 10, marginBottom: 5 }} />
        <View style={{ flex: 1 }}>
          <Navigation />
        </View>
      </View>
    </ConvexClientProvider>
  );
}
