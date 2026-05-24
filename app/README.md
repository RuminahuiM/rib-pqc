# app/

**Mobile-App** (React Native plus Expo SDK 51+ plus TypeScript).

Inhalt wird ab Sprint 1 aufgebaut. Geplante Struktur:

```
app/
├── package.json
├── tsconfig.json
├── app.json               # Expo config
├── app/                   # Expo Router screens
│   ├── _layout.tsx
│   ├── login.tsx
│   ├── home.tsx
│   └── profile.tsx
├── src/
│   ├── crypto/            # Crypto-Abstraction (@noble/post-quantum wrapping)
│   │   ├── kem.ts
│   │   ├── cipher.ts
│   │   ├── signature.ts
│   │   └── hash.ts
│   ├── context/
│   │   ├── AuthContext.tsx
│   │   └── SessionContext.tsx
│   ├── services/
│   │   └── secureClient.ts # HTTP-Wrapper mit auto-encrypt
│   └── config.ts          # Crypto-Algorithmus-Defaults
└── __tests__/
```

Bezug zu Backlog-Stories: siehe `../docs/09_product_backlog.md`, Epic APP, sowie Client-Teil von CRY und DCH.

Setup (vorläufig):

```bash
cd app
npm install
npx expo start
```

Test-Phone empfohlen: ein Gerät statt Simulator, weil die App native Crypto-Primitives nutzt (`react-native-get-random-values`).
