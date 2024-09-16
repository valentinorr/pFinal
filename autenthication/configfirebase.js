import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyAThk5LEH26TWY7Ry5SWi7Nk8_ezqLUJgQ",
  authDomain: "mondongo-abb0a.firebaseapp.com",
  projectId: "mondongo-abb0a",
  storageBucket: "mondongo-abb0a.appspot.com",
  messagingSenderId: "353548078833",
  appId: "1:353548078833:web:76b50830f972101f66a350"
};

// Inicializar Firebase
const app = initializeApp(firebaseConfig);

// Inicializar el servicio de autenticación
const auth = getAuth(app);

export { auth };
