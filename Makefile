help:
	@echo "Usage:"
	@echo "  make run-fit-accuracy   # Run FitAccuracy analysis"
	@echo "  make clean-reports      # Delete everything in reports/"

run-fit-accuracy:
	python -m src.features.fit_accuracy.run

clean-reports:
	rm -rf reports/*
	@echo "Reports have been cleaned 🧹"