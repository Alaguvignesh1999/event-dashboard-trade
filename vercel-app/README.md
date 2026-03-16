# Vercel App

This subfolder is the deployable web product for the event comparison dashboard.

## What it is

- `events.yaml` and `universal_preset_loader.py` are duplicated here so the app can build without reaching outside the subfolder.
- `scripts/export_dashboard_snapshot.py` generates static JSON snapshots into `public/data/`.
- The Next.js app reads only those generated JSON files at runtime.

## Local setup

1. Install Python dependencies:

   ```powershell
   pip install -r requirements-data.txt
   ```

2. Install Node dependencies:

   ```powershell
   npm install
   ```

3. Optional but recommended: set your FRED key for richer credit and breakeven coverage:

   ```powershell
   $env:FRED_API_KEY="your_fred_key_here"
   ```

4. Build the snapshot and start the app:

   ```powershell
   npm run build
   npm run start
   ```

## Vercel setup

- Import the repository or uploaded folder into Vercel.
- Set the Vercel project root directory to `vercel-app`.
- Add environment variable `FRED_API_KEY`.
- Use build command `npm run build`.

## Notes

- No secrets are stored in tracked files.
- `public/data/` is generated during the build step.
- The root notebook project remains the research workspace; this subfolder is the polished deployment target.
