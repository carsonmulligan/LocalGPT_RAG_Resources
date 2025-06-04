# SurvivalGPT RAG Resources

Pre-vectorized survival knowledge packages for offline mobile RAG systems.

## 📦 Available Packages

Check `rag_packages/catalog.json` for the complete list of available packages.

## 🔗 API Endpoints

- **Catalog**: `https://raw.githubusercontent.com/carsonmulligan/SurvivalGPT_RAG_Resources/main/rag_packages/catalog.json`
- **Package**: `https://raw.githubusercontent.com/carsonmulligan/SurvivalGPT_RAG_Resources/main/rag_packages/{package_id}/{file}`
- **iOS Config**: `https://raw.githubusercontent.com/carsonmulligan/SurvivalGPT_RAG_Resources/main/rag_packages/ios_config.json`

## 📱 iOS Integration

```swift
let ragManager = SurvivalRAGManager()
await ragManager.loadCatalog()
await ragManager.downloadPackage("fishing_basics")
let results = await ragManager.search("fishing knots")
```

## 📊 Package Sizes

- **Vector Databases**: Pre-computed embeddings (MLX format)
- **iOS Indices**: Keyword lookup for fast search
- **Total Size**: ~2-5MB per package vs 50MB+ raw PDFs

## 🔄 Updates

Packages are updated independently with version tracking and checksums for integrity verification.
