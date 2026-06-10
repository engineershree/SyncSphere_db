# DEPLOYMENT FIX PLAN

## 1. Exact Files Modified
- `runtime.txt` (NEW FILE)

## 2. Exact Code Changes
A new file named `runtime.txt` was added to the root directory with the following contents:
```text
python-3.11.11
```

No changes were made to existing application files (`app/main.py`, `app/schemas/*`, etc.).

## 3. Dependency Changes
- **None**. Pydantic remains at `1.10.13` and FastAPI remains at `0.104.1`. 
- By downgrading the Python runtime to 3.11 instead of upgrading the dependencies, we avoided refactoring the entire codebase to accommodate Pydantic v2 breaking changes.

## 4. Render Configuration Changes
- Render automatically detects the `runtime.txt` file at the root of a Python repository. 
- It will parse the file during the build phase and fetch the `python-3.11.11` runtime environment before executing `pip install -r requirements.txt`.
- No changes to the Render Dashboard "Build Command" or "Start Command" are required.

## 5. Rollback Procedure
If the deployment encounters an unexpected issue with Python 3.11.11:
1. Delete the `runtime.txt` file from the repository root:
   ```bash
   git rm runtime.txt
   git commit -m "chore: rollback runtime.txt"
   git push origin main
   ```
2. Trigger a manual deployment in the Render Dashboard to revert back to Render's default Python version.
