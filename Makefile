.PHONY: all vault clean

all: vault

vault: build/input.json cosense2obsidian.py
	python3 cosense2obsidian.py

build/input.json:
	@mkdir -p build
	@if [ -z "$$SCRAPBOX_PROJECT" ] || [ -z "$$SCRAPBOX_SESSION_ID" ]; then \
		echo "Error: SCRAPBOX_PROJECTとSCRAPBOX_SESSION_IDの環境変数を設定してください。"; \
		echo "例: export SCRAPBOX_PROJECT=your_project"; \
		echo "    export SCRAPBOX_SESSION_ID=xxxx"; \
		exit 1; \
	fi; \
	curl -s -H "Cookie: connect.sid=$$SCRAPBOX_SESSION_ID" "https://scrapbox.io/api/page-data/export/$$SCRAPBOX_PROJECT.json" -o build/input.json
analyze: build/input.json
	python3 cosense2obsidian_analyze_filename.py


clean:
	rm -rf build vault/*
