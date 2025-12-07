import { initializeApp } 
    from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";

import { 
  getFirestore, collection, addDoc, doc, setDoc, getDoc 
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";


  const firebaseConfig = {
    apiKey: "AIzaSyA9w211IS0nmwYNJ6YjHfk2kOQpjMd7n-4",
    authDomain: "hackathon-61f47.firebaseapp.com",
    projectId: "hackathon-61f47",
    storageBucket: "hackathon-61f47.firebasestorage.app",
    messagingSenderId: "758852476778",
    appId: "1:758852476778:web:9b60c385eaf564920c0f13",
    measurementId: "G-Y1CPKYX1BX"
  };

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
