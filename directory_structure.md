beer-tracker/
  .streamlit/
    config.toml
    secrets.toml            # (optional) for DB creds if you choose a hosted DB
  app.py                    # Streamlit entrypoint + routing between pages
  pages/
    1_Log_Beers.py          # page 1 UI: submit beers
    2_Stats.py              # page 2 UI: leaderboards + maps + fun stats
  backend/
    __init__.py
    db.py                   # storage layer (SQLite or Google Sheet)
    models.py               # dataclasses / validation helpers
    services.py             # ingest + stats computation
    stats.py                # leaderboard, heatmap prep, benchmarks
  assets/
    ground_rules.md         # displayed on Page 1
  data/
    beer_tracker.db         # local SQLite db (works locally; on Cloud may reset on redeploy)
  requirements.txt
  README.md
