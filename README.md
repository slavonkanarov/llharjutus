# Sõna demo

A small, runnable learner view for two Estonian exercises. The frontend and backend are separate services. The backend serves a published sample lesson, checks submissions, enforces two attempts, and reveals answers only after the final attempt.

## Run locally

Python 3.10+ is sufficient. Open two terminals in the repository root:

```bash
python -m backend.server
```

```bash
python -m frontend.server
```

Open [http://127.0.0.1:5173](http://127.0.0.1:5173). The frontend calls the backend at `http://127.0.0.1:8000`. Use **Начать демо заново** below the lesson to clear your demo attempts.

The AI service boundary can also be started with `python -m ai_service.server` on port 8001. The sample exercises disable AI review, so it is not required for this demo.

## Check

```bash
python -m unittest discover -s backend/tests -v
```

## Demo scope

The sample lesson and answer keys are separate backend modules. Attempts are held in memory and disappear when the backend restarts. The bundled learner tokens are demo credentials, not production authentication. The next implementation stage replaces the in-memory repository with MongoDB collections and adds authoring, publication controls, and MinIO-backed media. No media objects are used in this sample.
