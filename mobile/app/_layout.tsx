import {Stack} from "expo-router";
import {StatusBar} from "expo-status-bar";
import {GestureHandlerRootView} from "react-native-gesture-handler";
import {theme} from "../src/theme";
export default function Layout(){
 return <GestureHandlerRootView style={{flex:1,backgroundColor:theme.bg}}>
  <StatusBar style="light"/>
  <Stack screenOptions={{headerShown:false}}/>
 </GestureHandlerRootView>;
}
