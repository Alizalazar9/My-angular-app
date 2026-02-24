# My Angular App

Everything is organized in two folders: **client** (Angular UI) and **server** (Flask backend).

## Structure

```
client/              # Angular app – all UI
├── src/
├── public/
├── angular.json
├── package.json
└── dist/            # build output (after npm run build)

server/              # Flask backend – all server
├── server.py        # main API + serves client
├── manifest.json    # app data
├── build.py         # builds the exe
├── build.spec       # PyInstaller config
├── requirements.txt
├── downloads/       # optional: exe files for download endpoint
└── dist/            # AppStore.exe (after python server/build.py)
```

The exe bundles the built client and knows how to find it (bundled inside exe or in a `client/` folder next to the exe).

## Development

1. **Client** (from project root):
   ```bash
   cd client
   npm install
   npm run build
   ```

2. **Server** (from project root):
   ```bash
   pip install -r server/requirements.txt
   python server/server.py
   ```
   Opens http://127.0.0.1:5000

## Build exe

1. Build the client (see above).
2. From project root:
   ```bash
   python server/build.py
   ```
3. Run `server/dist/AppStore.exe`
