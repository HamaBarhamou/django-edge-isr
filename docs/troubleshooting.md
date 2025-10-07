# Troubleshooting

- **No settings configured**: set `DJANGO_SETTINGS_MODULE` or configure `EDGE_ISR`.
- **Redis errors**: check `REDIS_URL` and connectivity.
- **Headers missing**: ensure middleware is installed and decorator applied; check for other middlewares overriding `Cache-Control`.
- **CDN not purging**: verify credentials/zone/distribution and that you’re purging exact URLs.
- **Tests fail with “No module named 'tests'”**: run `python -m pytest` or ensure PYTHONPATH includes repo root.
