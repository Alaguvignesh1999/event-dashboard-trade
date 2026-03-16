# Event Comparison and Trade Idea Dashboard

Core project files:
- `Event Dashboard Universal v44.ipynb`
- `events.yaml`
- `universal_preset_loader.py`
- `requirements.txt`

Runtime/generated files:
- `_runtime/`

`_runtime/` is optional and safe to delete. The notebook will recreate cache and exported snapshot files there when needed.

Typical setup:

```bash
pip install -r requirements.txt
```

FRED setup in Windows PowerShell:

```powershell
$env:FRED_API_KEY="your_fred_api_key"
```

The notebook prefers `FRED_API_KEY` from the environment and only uses the notebook fallback if it is explicitly set to a non-placeholder value.
