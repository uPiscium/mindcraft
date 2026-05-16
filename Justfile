default: run

run *args:
  @echo "Running the application..."
  npx tsx main.js {{args}}
