import 'react-native-get-random-values'; 
// const { getRandomValues } = require('expo-crypto');
// import { getRandomValues } from 'expo-crypto';
import { Buffer } from 'buffer';
// import cloneDeep from "lodash.clonedeep";
import structuredClone from "realistic-structured-clone";



// import { getRandomValues as expoCryptoGetRandomValues } from 'expo-crypto';
// import { Buffer } from 'buffer';

global.Buffer = Buffer;



if (typeof global.structuredClone !== "function") {
  global.structuredClone = structuredClone as any;
}

// getRandomValues polyfill
// class Crypto {
//   getRandomValues = getRandomValues;
// }

// const webCrypto = typeof crypto !== 'undefined' ? crypto : new Crypto();

// (() => {
//   if (typeof crypto === 'undefined') {
//     Object.defineProperty(window, 'crypto', {
//       configurable: true,
//       enumerable: true,
//       get: () => webCrypto,
//     });
//   }
// })();



// import 'react-native-get-random-values'; // This sets up crypto.getRandomValues
// import { Buffer } from 'buffer';

// // Set Buffer globally
// global.Buffer = Buffer;