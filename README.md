## **📁 ESTRUTURA COMPLETA DOS ARQUIVOS PARA WINDOWS**

Crie a seguinte estrutura na sua máquina Windows:

```
C:\case-management\
├── backend\
│   ├── server.py        (código completo do servidor)
│   ├── requirements.txt (dependências Python)
│   └── .env            (configurações)
├── frontend\
│   ├── src\
│   │   ├── App.js      (aplicação React)
│   │   ├── App.css     (estilos)
│   │   └── index.js    (ponto de entrada)
│   ├── public\
│   │   └── index.html  (HTML base)
│   ├── package.json    (dependências Node.js)
│   ├── tailwind.config.js
│   └── .env           (configurações frontend)
```

## **🔧 ARQUIVOS DE CONFIGURAÇÃO**

**1. Backend `.env`:**
```env
MONGO_URL=mongodb://localhost:27017
```

**2. Frontend `.env`:**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

**3. Frontend `public/index.html`:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Case Management System</title>
</head>
<body>
    <div id="root"></div>
</body>
</html>
```

**4. Frontend `src/index.js`:**
```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './App.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

**5. Frontend `tailwind.config.js`:**
```javascript
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

## **🚀 COMANDOS PARA EXECUTAR**

**Abra 3 terminais (Command Prompt ou PowerShell):**

**Terminal 1 - MongoDB:**
```cmd
# Se instalou MongoDB localmente:
mongod

# OU use uma connection string do MongoDB Atlas no .env
```

**Terminal 2 - Backend:**
```cmd
cd C:\case-management\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

**Terminal 3 - Frontend:** 
```cmd
cd C:\case-management\frontend
npm install
npm start
```

## **🌐 ACESSO AO SISTEMA**

Após executar tudo:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001

## **👤 CONTAS DEMO**
- **Admin**: admin / admin123
- **Registrar**: registrar1 / reg123  
- **Assistant**: assistant1 / ass123
- **Lawyer**: lawyer1 / law123

## **💡 DICAS PARA WINDOWS**

1. **MongoDB Cloud (Recomendado)**: Ao invés de instalar MongoDB localmente, use MongoDB Atlas (gratuito)
2. **Python Path**: Verifique se Python está no PATH do sistema
3. **Node.js**: Instale a versão LTS mais recente
4. **Firewall**: Pode precisar permitir as portas 3000 e 8001

Precisa de ajuda com algum passo específico da instalação no Windows?
