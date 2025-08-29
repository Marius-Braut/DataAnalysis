# -----------------------------
# Makefile for DataAnalysis
# -----------------------------

.PHONY: help run-fit-accuracy run-scans-performance clean-reports \
        clean-fit-accuracy clean-scans-performance \
        rerun-fit-accuracy rerun-scans-performance

help:
	@echo "Usage:"
	@echo "  make run-fit-accuracy"
	@echo "  make run-scans-performance start=YYYY-MM-DD end=YYYY-MM-DD [top_org=NAME]"
	@echo "  make clean-reports analysis=<AnalysisName>"
	@echo "  make rerun-fit-accuracy"
	@echo "  make rerun-scans-performance start=YYYY-MM-DD end=YYYY-MM-DD [top_org=NAME]"

# -----------------------------
# Run analyses
# -----------------------------

run-fit-accuracy:
	python -m src.features.fit_accuracy.run
	@echo "✅ FitAccuracy analysis ran successfully. Outputs: reports/FitAccuracy"

run-scans-performance:
	@if [ -z "$(start)" ] || [ -z "$(end)" ]; then \
		echo "❌ Please provide start and end: make run-scans-performance start=YYYY-MM-DD end=YYYY-MM-DD [top_org=NAME]"; \
		exit 1; \
	fi
	python -m src.features.scans_performance.run --start-date $(start) --end-date $(end) $(if $(top_org),--top-org "$(top_org)",)
	@echo "✅ ScansPerformance analysis ran successfully for $(start) → $(end). Outputs: reports/ScansPerformance"

# -----------------------------
# Clean reports (scoped)
# -----------------------------

clean-reports:
	@if [ -z "$(analysis)" ]; then \
		echo "❌ Please specify which analysis to clean, e.g. make clean-reports analysis=FitAccuracy"; \
		exit 1; \
	fi
	rm -rf reports/$(analysis)/*
	@echo "🧹 Reports for $(analysis) have been cleaned ✅"

# Convenience cleaners for common analyses
clean-fit-accuracy:
	$(MAKE) clean-reports analysis=FitAccuracy

clean-scans-performance:
	$(MAKE) clean-reports analysis=ScansPerformance

# -----------------------------
# Rerun = clean + run
# -----------------------------

rerun-fit-accuracy: clean-fit-accuracy run-fit-accuracy

rerun-scans-performance:
	@if [ -z "$(start)" ] || [ -z "$(end)" ]; then \
		echo "❌ Please provide start and end: make rerun-scans-performance start=YYYY-MM-DD end=YYYY-MM-DD [top_org=NAME]"; \
		exit 1; \
	fi
	$(MAKE) clean-scans-performance
	$(MAKE) run-scans-performance start=$(start) end=$(end) $(if $(top_org),top_org="$(top_org)",)