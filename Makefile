.PHONY: audit build demo test app

audit:
	python3 scripts/audit_datasets.py

build:
	python3 scripts/build_processed_data.py

demo: build
	python3 scripts/export_demo_assets.py

test:
	pytest

app:
	streamlit run app/streamlit_app.py
