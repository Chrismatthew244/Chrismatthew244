- 👋 Hi, I’m @Chrismatthew244
- 👀 I’m interested in OSINT
- 🌱 I’m currently learning phyton
- 💞️ I’m looking to collaborate on OSINT
- 📫 How to reach me chrismatthew244@protonmail.com

<!---
Chrismatthew244/Chrismatthew244 is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->

## Document Service

This repository contains a simple FastAPI application that allows authorized users to upload, preview and delete documents. Files are stored on the local filesystem by default and can optionally be stored on Amazon S3.

### Running locally

```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Set the `API_KEY` environment variable and include it in requests using the `X-API-Key` header. The service also respects `DATABASE_URL`, `STORAGE_DIR` and `S3_BUCKET` environment variables for custom configuration.
