import React from 'react'
import { KeyboardAwareScrollView } from 'react-native-keyboard-aware-scroll-view'

interface KeyboardViewProps { 
    children: React.ReactNode,
    style?: any

}
const KeyboardView = ({children, style}: KeyboardViewProps) => {
  return (
  <KeyboardAwareScrollView
        style={{flex: 1, ...style}}
        resetScrollToCoords={{ x: 0, y: 0 }}
        contentContainerStyle={{ flexGrow: 1 }}
        scrollEnabled={true}
        enableOnAndroid={true}
        enableAutomaticScroll={true}
        extraHeight={100}
      >
          
{children}

      </KeyboardAwareScrollView>
  )
}

export default KeyboardView