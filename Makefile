# Default target
help:
	@echo "Available targets:"
	@echo "  make run-fit-accuracy start=YYYY-MM-DD end=YYYY-MM-DD"

# Run Fit Accuracy analysis
run-fit-accuracy:
	python src/features/fit_accuracy/run.py --start $(start) --end $(end)
